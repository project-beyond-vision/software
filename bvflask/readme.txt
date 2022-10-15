1. install virtual env following the guide here
    https://phoenixnap.com/kb/install-flask
2. create a venv in the environment
3. activate it (instructions are still in the site linked)
    - on windows go to /.venv/Scripts and source Activate.ps1
4. dont forget to install sqlalchemy for the database 
    pip install Flask-SQLAlchemy 
5. to start the server type in
    python -m flask run

test.py is used to test whether the POST request works with the API route

TODO: create front end for data visualization