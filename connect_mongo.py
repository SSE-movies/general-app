from pymongo import MongoClient

# Replace <password> with your actual password
MONGO_URI = "mongodb+srv://admin:LKt2lujE6czy468S@userauthcluster.obo8e.mongodb.net/?retryWrites=true&w=majority&appName=UserAuthCluster"

# Create a MongoDB client
client = MongoClient(MONGO_URI)

# Connect to a database
db = client["test_database"]  # Replace with your database name

# Create a test collection
collection = db["test_collection"]

# Insert a test document
collection.insert_one({"name": "Test User", "email": "test@example.com"})

# Fetch and print the document
print(collection.find_one({"name": "Test User"}))

# Close the connection
client.close()
