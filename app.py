from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from functools import wraps
import os
from bson.objectid import ObjectId 

app = Flask(__name__, 
    template_folder='src/templates',
    static_folder='src/static')

# Configuration
app.config["SECRET_KEY"] = os.urandom(24)
app.config["MONGO_URI"] = "mongodb://localhost:27017/auth_system"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})  # Convert string ID to ObjectId
        if not user or not user.get('is_admin'):
            return redirect(url_for('login'))  # Redirect instead of showing error
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': request.form['username']})
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)  # Store admin status in session
            
            if user.get('is_admin'):
                return redirect(url_for('admin'))
            return redirect(url_for('search'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    existing_user = mongo.db.users.find_one({'username': request.form['username']})
    if existing_user:
        return 'Username already exists', 400
    
    hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    user = {
        'username': request.form['username'],
        'password': hashed_password,
        'is_admin': False
    }
    mongo.db.users.insert_one(user)
    return redirect(url_for('login'))

@app.route('/search')
@login_required
def search():
    return render_template('search.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin():
    # Fetch all users, excluding password
    users = list(mongo.db.users.find({}, {'password': 0}))
    
    # Convert ObjectId to string
    for user in users:
        user['_id'] = str(user['_id'])
    
    return render_template('admin.html', 
                           username=session.get('username'), 
                           users=users)

# API Routes for admin functionality
@app.route('/api/users')
@admin_required
def get_users():
    users = list(mongo.db.users.find({}, {'password': 0}))
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users)

@app.route('/api/users/<user_id>/reset-password', methods=['POST'])
@admin_required
def reset_password(user_id):
    try:
        # Get new password from request
        new_password = request.json.get('newPassword')
        
        if not new_password:
            return jsonify({'error': 'New password is required'}), 400
        
        # Hash the new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update user's password
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)}, 
            {'$set': {'password': hashed_password}}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'error': 'User not found or password unchanged'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/username', methods=['PUT'])
@admin_required
def update_username(user_id):
    new_username = request.json.get('newUsername')
    mongo.db.users.update_one(
        {'_id': user_id}, 
        {'$set': {'username': new_username}}
    )
    return 'Username updated'

@app.route('/api/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        # Convert string ID to ObjectId
        result = mongo.db.users.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count > 0:
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '_main_':
    app.run(debug=True)