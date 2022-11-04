from datetime import datetime
from flask import Flask, render_template, request, jsonify
import json
import os

import numpy as np
import random

from flask_sqlalchemy import SQLAlchemy

import folium
from folium.plugins import HeatMap
import branca

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(os.getcwd(), 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

predlist = []

ACTION_ID_TO_STRING = ('sitting', 'getting up', 'climbing stairs', 'walking')
FALL_ID_TO_STRING = ('forward', 'left', 'right', 'backward')

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
        pred5 = entry["pred5"]
        pred6 = entry["pred6"]
        pred7 = entry["pred7"]
        pred8 = entry["pred8"]
        pred9 = entry["pred9"]

        all_prev_acts = [pred1, pred2, pred3, pred4, pred5, pred6, pred7, pred8, pred9]
        prev_pred = max(set(all_prev_acts), key=lambda i: all_prev_acts.count(i) + random.random())

        pred10 = entry["pred10"]
        is_panic = entry["is_panic"]
        is_flame = entry["is_flame"]

        lat = entry["lat"]
        long = entry["long"]
        time = datetime.fromisoformat(entry["time"])
        entry_db = Entry(time, lat, long, is_panic, is_flame, pred1, pred2, pred3, pred4, pred5, pred6, pred7, pred8, pred9, prev_pred, pred10)
        db.session.add(entry_db)
        db.session.commit()
        print("Entry added to the database!", entry)
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    except Exception as e:
        print(e)
        return json.dumps({'success':False}), 500, {'ContentType':'application/json'} 


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

    latlongmeans = np.array(list(zip(lats, longs)))
    print(latlongmeans.shape)
        

    # Place center of map in the middle of all falls
    lat = np.mean(latlongmeans[:, 0])
    long = np.mean(latlongmeans[:, 1])
    startingLocation = [lat, long]
    print(startingLocation)

    hmap = folium.Map(location=startingLocation, zoom_start=12)

    title = 'Heatmap of Aggregated Falls per Unit Area'
    title_html = f'''
             <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
             '''
    hmap.get_root().html.add_child(folium.Element(title_html))

    steps=20
    colormap = branca.colormap.linear.RdPu_09.to_step(steps)
    gradient_map={}
    for i in range(steps):
        gradient_map[1/steps*i] = colormap.rgb_hex_str(1/steps*i)
    colormap.caption = 'Density of Falls'
    colormap.add_to(hmap) #add color bar at the top of the map


    hm_wide = HeatMap( latlongmeans,
                        min_opacity=0.2,
                        radius=17, blur=15,
                        max_zoom=1,
                        gradient=gradient_map)

    # Adds the heatmap element to the map
    hmap.add_child(hm_wide)

    # Saves the map to heatmap.hmtl
    # hmap.save(os.path.join('./templates', 'heatmap.html'))
    #Render the heatmap
    return render_template('heatmap.html')

@app.route('/bar')
def bar():
    entries = db.session.query(Entry)

    prev_acts = []
    fall_types = [] 
    panics = []
    flames = []

    for e in entries:
        prev_acts.append(e.prev_pred)
        fall_types.append(e.pred10)
        panics.append(e.is_panic)
        flames.append(e.is_flame)

    prev_acts_lst = np.array(prev_acts)
    n = prev_acts_lst.shape[0]
    prev_acts, prev_act_counts = np.unique(prev_acts_lst, return_counts=True)

    fall_types_lst = np.array(fall_types)
    fall_types, fall_type_counts = np.unique(fall_types_lst, return_counts=True)

    n_panics = sum(panics)
    n_flames = sum(flames)

    data = [
        {
            'title': 'Actions Before Falling',
            'description': 'What are people doing before they fall? Here are the stats.',
            'labels': [ACTION_ID_TO_STRING[i] for i in prev_acts],
            'counts': prev_act_counts,
            'chart_name': 'action_chart'
        },
        {
            'title': 'Types of Falls',
            'description': 'How are they falling? Forward? To the side?',
            'labels': [FALL_ID_TO_STRING[i] for i in fall_types],
            'counts': fall_type_counts,
            'chart_name': 'fall_type_chart'
        },
        {
            'title': 'Panic or Flame?',
            'description': 'Did they already feel something was wrong? Did they press the panic button? Was there a fire?',
            'labels': ['panic', 'no panic', 'fire', 'no fire'],
            'counts': [n_panics, n - n_panics, n_flames, n - n_flames],
            'chart_name': 'panic_fire_chart'
        }
    ]

    return render_template('bar_chart.html', data=data)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, unique=False, nullable=False)
    lat = db.Column(db.Float, unique=False, nullable=False)
    long = db.Column(db.Float, unique=False, nullable=False)
    is_panic = db.Column(db.Boolean, unique=False, nullable=False)
    is_flame = db.Column(db.Boolean, unique=False, nullable=False)
    pred1 = db.Column(db.Integer, unique=False, nullable=False)
    pred2 = db.Column(db.Integer, unique=False, nullable=False)
    pred3 = db.Column(db.Integer, unique=False, nullable=False)
    pred4 = db.Column(db.Integer, unique=False, nullable=False)
    pred5 = db.Column(db.Integer, unique=False, nullable=False)
    pred6 = db.Column(db.Integer, unique=False, nullable=False)
    pred7 = db.Column(db.Integer, unique=False, nullable=False)
    pred8 = db.Column(db.Integer, unique=False, nullable=False)
    pred9 = db.Column(db.Integer, unique=False, nullable=False)
    prev_pred = db.Column(db.Integer, unique=False, nullable=False)
    pred10 = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, time, lat, long, is_panic, is_flame, pred1, pred2, pred3, pred4, pred5, pred6, pred7, pred8, pred9, prev_pred, pred10):
        self.time = time
        self.lat = lat
        self.long = long
        self.is_panic = is_panic
        self.is_flame = is_flame
        self.pred1 = pred1
        self.pred2 = pred2
        self.pred3 = pred3
        self.pred4 = pred4
        self.pred5 = pred5
        self.pred6 = pred6
        self.pred7 = pred7
        self.pred8 = pred8
        self.pred9 = pred9
        self.prev_pred = prev_pred
        self.pred10 = pred10

    def __repr__(self):
        return '<id %r>' % self.time

if __name__ == '__main__':
    with app.app_context(): #uncomment these 2 lines to instantiate db
        db.create_all()
    app.run(debug=True)