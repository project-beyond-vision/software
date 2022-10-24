from datetime import datetime
from statistics import mean
from flask import Flask, render_template, request, jsonify
import json
import os

import numpy as np
from sklearn.mixture import GaussianMixture

from flask_sqlalchemy import SQLAlchemy

import folium
from folium.plugins import HeatMap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(os.getcwd(), 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

predlist = []

actions = ('walking', 'jogging', 'running', 'stairs')

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
        # print(entry["time"])
        time = datetime.fromisoformat(entry["time"])
        # print(type(time))
        entry = Entry(time, lat, long, pred1, pred2, pred3, pred4)
        db.session.add(entry)
        db.session.commit()
        # print(entry.id)
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    except Exception as e:
        print(e)
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 


@app.route('/drawMap')
def draw_map():
    entries = db.session.query(Entry)
    lats = []
    longs = []
    preds = []

    for entry in entries:
        # Collate locations of falls
        lats.append(entry.lat)
        longs.append(entry.long)
        preds.append(entry.pred4)

    X = np.array(list(zip(lats, longs)))
    n = 4
    gm = GaussianMixture(n).fit(X)
    data_clusters = gm.predict(X)
    unique, counts = np.unique(data_clusters, return_counts=True)

    d = dict(zip(unique, counts))

    latlongmeans = gm.means_
    print(latlongmeans)
    latlongmeans = np.c_[latlongmeans, np.zeros(n)]
    for i in range(n):
        latlongmeans[i, 2] = d.get(i, 0)
        

    # Place center of map in the middle of all falls
    lat = np.mean(latlongmeans[:, 0])
    long = np.mean(latlongmeans[:, 1])
    startingLocation = [lat, long]
    print(startingLocation)
    hmap = folium.Map(location=startingLocation, zoom_start=15)

    hm_wide = HeatMap( latlongmeans,
                        min_opacity=0.2,
                        radius=17, blur=15,
                        max_zoom=1)

    # Adds the heatmap element to the map
    hmap.add_child(hm_wide)
    # Saves the map to heatmap.hmtl
    hmap.save(os.path.join('./templates', 'heatmap.html'))
    #Render the heatmap
    return render_template('heatmap.html')

@app.route('/bar')
def bar():
    entries = db.session.query(Entry)
    prev_acts = {}

    for entry in entries:
        # Collate prev actions
        all_prev_acts = [entry.pred1, entry.pred2, entry.pred3]
        common_act = max(set(all_prev_acts), key=all_prev_acts.count)
        common_act = actions[common_act]
        if common_act not in prev_acts:
            prev_acts[common_act] = 0
        prev_acts[common_act] += 1

    bar_labels=prev_acts.keys()
    bar_values=prev_acts.values()
    return render_template('bar_chart.html', title='Actions before falling', max=max(bar_values), labels=bar_labels, values=bar_values)


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