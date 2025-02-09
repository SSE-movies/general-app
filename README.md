# SSE_ProjectII

### GitHub
Clone the repository
```
git clone https://gitlab.doc.ic.ac.uk/lab2425_spring/intro2ml_cw1_12.git
```
Push Changes to GitHub
```
$ git push origin main
```

Pull Latest Changes
```
$ git pull
```


## Creating virtual environment
Create the venv
```
$ python3 -m venv venv
```

Activate venv
```
$ source venv/bin/activate
```

Install Flask
```
$ pip install flask
```

## Run Flask App
Be careful, the port may have been changed
```
$ flask --app app.py run --host=0.0.0.0 --port 8000
```

