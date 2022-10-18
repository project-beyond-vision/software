from datetime import datetime
from statistics import mean
from flask import Flask, render_template, request, jsonify
import json
import os

from flask_sqlalchemy import SQLAlchemy

import folium
from folium.plugins import HeatMap

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

@app.route('/hello')
def get_entries():
    entry = db.session.query(Entry)
    print(entry.time)
    print(entry)
    return str(entry)

@app.route('/drawMap')
def draw_map():
    # map_data = pd.read_csv("./Data/data_01.csv", sep=';')
    entries = db.session.query(Entry)
    lats = []
    longs = []
    preds = []
    for entry in entries:
        lats.append(entry.lat)
        longs.append(entry.long)
        preds.append(entry.pred4)
    lat = mean(lats)
    long = mean(longs)
    startingLocation = [lat, long]#[39.47, -0.37]
    hmap = folium.Map(location=startingLocation, zoom_start=15)
    # max_amount = map_data['RelacionPrecioTamanio'].max()
    hm_wide = HeatMap( list(zip(lats, longs, preds)),
                        min_opacity=0.2,
                        max_val=5,
                        radius=17, blur=15,
                        max_zoom=1)

    # Adds the heatmap element to the map
    hmap.add_child(hm_wide)
    # Saves the map to heatmap.hmtl
    hmap.save(os.path.join('./templates', 'heatmap.html'))
    #Render the heatmap
    return render_template('heatmap.html')


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
        return '<id %r>' % self.time

if __name__ == '__main__':
    with app.app_context(): #uncomment these 2 lines to instantiate db
        db.create_all()
    app.run(debug=True)