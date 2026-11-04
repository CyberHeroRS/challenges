from flask import Flask, render_template, url_for, request, make_response, redirect, session, Response
from markupsafe import escape
import json
import uuid
import os
import base64
import socket
import time
import xml.etree.ElementTree as ET
from lxml import etree
import requests
import io

import psycopg2

app = Flask(__name__, template_folder='templates')
app.secret_key = 'slkwqhedkbwdboihu23i23bo2ub3b24ifn3i4ubfi24z2v3ejhbfiuwhveuziwqvbehf'
app.config['SESSION_COOKIE_HTTPONLY'] = True
ADMIN_BOT_HOST = 'admin-bot'
_BOT_IP_CACHE = None


def encode_user_ip(value):
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def decode_user_ip(value):
    try:
        return base64.b64decode(value.encode("ascii")).decode("utf-8")
    except Exception:
        return value


def get_admin_bot_ip():
    global _BOT_IP_CACHE
    if _BOT_IP_CACHE:
        return _BOT_IP_CACHE
    try:
        _BOT_IP_CACHE = socket.gethostbyname(ADMIN_BOT_HOST)
    except Exception:
        _BOT_IP_CACHE = None
    return _BOT_IP_CACHE


@app.before_request
def restrict_admin_routes():
    protected_paths = {'/admin/login', '/admin/contacts'}
    if request.path.startswith('/admin/contact'):
        protected_paths.add('/admin/contact')

    if request.path in protected_paths or request.path.startswith('/admin/contact'):
        bot_ip = get_admin_bot_ip()
        if not bot_ip or request.remote_addr != bot_ip:
            return "Forbidden", 403


@app.after_request
def add_user_ip_header(response):
    raw_user_ip = request.headers.get("X-User-IP") or request.remote_addr
    encoded_user_ip = encode_user_ip(raw_user_ip)
    response.headers["X-User-IP"] = encoded_user_ip
    response.set_cookie("user_ip", encoded_user_ip, httponly=True)
    return response


@app.context_processor
def inject_admin_state():
    return {
        'is_admin': session.get('is_admin', False),
        'admin_username': session.get('admin_username')
    }


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        dbname=os.getenv('POSTGRES_DB', 'webapp'),
        user=os.getenv('POSTGRES_USER', 'webapp'),
        password=os.getenv('POSTGRES_PASSWORD', 'webapp'),
    )

def init_db():
    conn = get_db_connection()
    conn.autocommit = True
    cur = conn.cursor()


    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        ON CONFLICT (username) DO UPDATE
        SET password = EXCLUDED.password
        """,
        ('admin', 'DragonSecSuperSecretPassword!')
    )
    
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id UUID PRIMARY KEY,
            url TEXT NOT NULL,
            email TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            user_ip TEXT NOT NULL
        )
        """
    )

    cur.execute("TRUNCATE TABLE contacts")


    cur.close()
    conn.close()


def init_db_with_retry(max_attempts=10, delay_seconds=1):
    last_error = None
    for _ in range(max_attempts):
        try:
            init_db()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(delay_seconds)
    raise last_error



@app.route('/')
def index():
    user_ip = request.remote_addr
    response = make_response(render_template('home.html'))
    response.headers["X-User-IP"] = user_ip
    return response


@app.route('/services')
def services():
    user_ip = request.remote_addr
    response = make_response(render_template('services.html'))
    response.headers["X-User-IP"] = user_ip
    return response


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = escape(request.form['email'])
        title = escape(request.form['title'])
        message = escape(request.form['message'])

        header_ip = request.headers.get("X-User-IP")
        cookie_ip = request.cookies.get("user_ip")
        raw_user_ip = decode_user_ip(header_ip) if header_ip else None
        if not raw_user_ip and cookie_ip:
            raw_user_ip = decode_user_ip(cookie_ip)
        if not raw_user_ip:
            raw_user_ip = request.remote_addr

        user_ip = encode_user_ip(raw_user_ip)
        
        submission_id = str(uuid.uuid4())

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO contacts (id, url, email, title, message, user_ip)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (submission_id, 'http://web-app:5000/submission/' + submission_id, email, title, message, user_ip)
        )
        conn.commit()
        cur.close()
        conn.close()

        contact_url = f"http://web-app:5000/admin/contact/{submission_id}"
        try:
            response = requests.post("http://admin-bot:3000/visit", json={"url": contact_url})
        except:
            return 500, "Couldnt send data to bot"

        resp = redirect(url_for('public_submission', submission_id=submission_id))
        return resp

    elif request.method == 'GET':
        response = make_response(render_template('contact.html'))
        return response

@app.route('/admin/contact/<submission_id>')
def view_submission(submission_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT url, email, title, message, user_ip
        FROM contacts
        WHERE id = %s
        LIMIT 1
        """,
        (submission_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return "Submission not found", 404

    data = {
        'email': row[1],
        'title': row[2],
        'message': row[3],
        'user_ip': decode_user_ip(row[4]),
        'url': row[0]
    }

    response = make_response(render_template('submission.html', data=data, submission_id=submission_id))
    return response


@app.route('/submission/<submission_id>')
def public_submission(submission_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT url, email, title, message, user_ip
        FROM contacts
        WHERE id = %s
        LIMIT 1
        """,
        (submission_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return "Submission not found", 404

    data = {
        'email': row[1],
        'title': row[2],
        'message': row[3],
        'user_ip': decode_user_ip(row[4]),
        'url': row[0]
    }

    response = make_response(render_template('submission.html', data=data, submission_id=submission_id))
    return response

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, username
            FROM users
            WHERE username = %s AND password = %s
            LIMIT 1
            """,
            (username, password)
        )
        admin_user = cur.fetchone()
        cur.close()
        conn.close()

        if admin_user:
            session['is_admin'] = True
            session['admin_username'] = admin_user[1]
            return redirect(url_for('admin_profile'))

        return render_template('admin_login.html', error='Invalid username or password')

    return render_template('admin_login.html')


@app.route('/admin/contacts', methods=['GET', 'POST'])
def admin_profile():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    if request.method == "GET":
        return render_template('admin_contact.html', 
                             username=session.get('admin_username', 'admin'),
                             search_results=[],
                             search_email="")

    if request.method == "POST":
        try:
            xml_data = request.data

            
            xparse = etree.XMLParser(resolve_entities=True)
            
            root = etree.fromstring(xml_data, xparse)
            
            email_elems = root.findall('.//email')
            if email_elems and email_elems[0].text:
                email = email_elems[0].text.strip()
                
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, email
                    FROM contacts
                    WHERE email LIKE %s
                    """,
                    (f"%{email}%",)
                )
                results = cur.fetchall()
                cur.close()
                conn.close()
                
                response_text = f"You searched for: {email}\n\n"
                for result in results:
                    response_text += f"UUID: {result[0]}, Email: {result[1]}\n"
                
                return Response(response_text, mimetype="text/plain")
            
            return Response("Error: No email element found", mimetype="text/plain"), 400
            
        except Exception as e:
            return Response(f"XML parsing error: {str(e)}", mimetype="text/plain"), 400
        

if __name__ == '__main__':
    try:
        init_db_with_retry()
    except Exception as e:
        print('Warning: init_db failed during startup:', e)
    app.run(debug=True, host='0.0.0.0')