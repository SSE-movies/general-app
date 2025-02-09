# SSE_ProjectII

## GitHub
Clone the repository
```
git clone https://github.com/tiagoriely/SSE_ProjectII.git
```
Push Changes to GitHub
```
git add .
git commit -m "Commit message"
git push origin main
```

Pull Latest Changes
```
git pull
```

### Using branches
#### Making changes
Create a branch
```
git checkout -b [branch_name]
```

List all branches
```
git branch
```

Switch between branches
```
git checkout main
git checkout [branch_name]
```

Check the status of your working directory
```
git status
```

Stage and commit changes
```
git add .
git commit -m "Descriptive commit message"
```

Push changes to remote; set an upstream branch like the below
```
git push -u origin [branch_name]
```

#### Keeping your branch updated
Fetch the latest changes
```
git fetch origin
```

Rebase your branch on latest main
```
git checkout [branch_name]
git rebase origin/main
```

Resolve conflicts if any
```
git add .
git rebase --continue
```

## Creating virtual environment
Create the venv
```
python3 -m venv venv
```

Activate venv
(Linux)
```
source venv/bin/activate
```
(Windows)
```
venv\Scripts\activate
```

Install packages
```
pip install -r requirements.txt
```

Add new dependencies to requirements.txt
```
pip freeze > requirements.txt
```

## Run Flask App
Set the Flask app
```
export FLASK_APP=app.py
```

Be careful, the port may have been changed
```
flask --app app.py run --host=0.0.0.0 --port 8000
```

