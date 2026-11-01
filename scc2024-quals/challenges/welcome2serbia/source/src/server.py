from flask import Flask, render_template, request, abort, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/city')
def city():
    city_name = request.args.get('file')
    city_name = city_name.replace('../', '')
    if city_name:
        file_path = os.path.join(app.root_path, 'cities', f'{city_name}')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            city_name = city_name.split('.')[0].lower()
            return render_template('city.html', content=content, city=city_name, image=f'/static/{city_name}.jpg')
        else:
            abort(404)
    else:
        return "No city specified", 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3500)