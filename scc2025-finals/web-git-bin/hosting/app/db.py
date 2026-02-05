import yaml
import os
import threading
import bcrypt
import sys

# Yes, YAML is weird to use as a DB, but it's simple and works for this case - we also made it thread-safe.

DATABASE = '/data/db/database.yml'
db_lock = threading.RLock()

def get_db():
    with db_lock:
        if not os.path.exists(DATABASE):
            with open(DATABASE, 'w') as f:
                yaml.safe_dump({'repos': []}, f)
        with open(DATABASE, 'r') as f:
            db = yaml.safe_load(f)
        return db

def save_db(db):
    with db_lock:
        with open(DATABASE, 'w') as f:
            yaml.safe_dump(db, f)

def validate_password(repo_name, password):
    with db_lock:
        db = get_db()
        for repo in db['repos']:
            if repo['name'] == repo_name:
                # Compare the hashed password
                return bcrypt.checkpw(password.encode('utf-8'), repo['password'].encode('utf-8'))
        return False

def add_repo(repo_name, password):
    with db_lock:
        db = get_db()
        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db['repos'].append({'name': repo_name, 'password': hashed_password})
        save_db(db)

def remove_repo(repo_name):
    with db_lock:
        db = get_db()
        db['repos'] = [repo for repo in db['repos'] if repo['name'] != repo_name]
        save_db(db)
