from flask import Flask

app = Flask(__name__)

ORACLE = False 

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route('/hit')
def hit():
    global ORACLE 

    ORACLE = True

    return '1337'

@app.route("/poll")
def poll():
    global ORACLE 

    if ORACLE:
        ORACLE = False
        return "1"
    else:
        return "0"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9999, debug=True)