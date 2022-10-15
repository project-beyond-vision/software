from datetime import datetime
from flask import Flask, render_template, request, jsonify
import json
import os

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(os.getcwd(), 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

predlist = []

@app.route('/')
def index():
    # dashboard should return heat map of falls
    # query the data first
    return render_template('dashboard.html')

@app.route('/store', methods=["POST"])
def store():
    # stores in data from the route as a POST request
    entry = json.loads(request.data.decode('utf-8'))
    try:
        pred1 = entry["pred1"]
        pred2 = entry["pred2"]
        pred3 = entry["pred3"]
        pred4 = entry["pred4"]
        lat = entry["lat"]
        long = entry["long"]
        print(entry["time"])
        time = datetime.fromisoformat(entry["time"])
        print(type(time))
        entry = Entry(time, lat, long, pred1, pred2, pred3, pred4)
        db.session.add(entry)
        db.session.commit()
        print(entry.id)
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    except Exception as e:
        print(e)
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 
        


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, unique=False, nullable=False)
    lat = db.Column(db.Float, unique=False, nullable=False)
    long = db.Column(db.Float, unique=False, nullable=False)
    pred1 = db.Column(db.Integer, unique=False, nullable=False)
    pred2 = db.Column(db.Integer, unique=False, nullable=False)
    pred3 = db.Column(db.Integer, unique=False, nullable=False)
    pred4 = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, time, lat, long, pred1, pred2, pred3, pred4):
        self.time = time
        self.lat = lat
        self.long = long
        self.pred1 = pred1
        self.pred2 = pred2
        self.pred3 = pred3
        self.pred4 = pred4

    def __repr__(self):
        return '<id %r>' % self.id

if __name__ == '__main__':
    with app.app_context(): #uncomment these 2 lines to instantiate db
        db.create_all()
    app.run(debug=True)