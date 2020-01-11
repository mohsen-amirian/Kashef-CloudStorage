import json
import os
import random
import string

from flask import Flask, url_for, send_from_directory
from flask.views import request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={
    r"/upload/*": {"origins": "*"},
    r"/serv/*": {"origins": "*"}
})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# app.config['SERVER_NAME'] = 'localhost:5000'
app.config['DEBUG'] = True
db = SQLAlchemy(app)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1080), unique=False, nullable=False)
    dir = db.Column(db.String(20), unique=True, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=False)


db.create_all()


@app.route('/upload/', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "پارامتر «file» در درخواست موجود نیست.", 400
    f = request.files['file']
    if f.filename == '':
        return "فایل انتخاب نشده است.", 400
    
    min_char = 8
    max_char = 12
    myChars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    dirname = "".join(random.choice(myChars) for x in range(random.randint(min_char, max_char)))
    os.makedirs(os.path.join('static', dirname))
    filename = os.path.join('static', dirname, f.filename)
    f.save(filename)

    db.session.add(
        File(name=f.filename, dir=dirname, size=os.stat(filename).st_size)
    )
    db.session.commit()
    return json.dumps({'url': url_for('serv', path=os.path.join(dirname, f.filename).replace('\\', '/'), _external=True)})


@app.route('/check/', methods=['POST'])
def check():
    if 'name' not in request.form and 'size' not in request.form:
        return "پارامترهای وارد شده مجاز نیستند.", 400

    for qf in File.query.filter_by(name=request.form['name'], size=request.form['size']):
        return json.dumps({'url': url_for('serv', path=os.path.join(qf.dir, qf.name), _external=True)})
    return "فایل یافت نشد.", 404

@app.route('/serv/<path:path>', methods=['GET'])
def serv(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
