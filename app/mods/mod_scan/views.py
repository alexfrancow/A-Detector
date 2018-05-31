# -*- encoding: utf-8 -*-
"""
A-Detector
Licence: GPLv3
Autor: @alexfrancow
"""

#################
#### imports ####
#################

import os
from flask import Flask, jsonify, Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

# Anomalies map
import json
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.plotly as py
from plotly.graph_objs import *
import re
from urllib.request import urlopen
import numpy as np
from flask import jsonify
import urllib

import pandas as pd
from sqlalchemy import create_engine
import datetime as dt

# Isolation Forest
from app.mods.mod_scan.isolation_forest import isolation_forest

################
#### config ####
################

scan_blueprint = Blueprint('scan', __name__, template_folder='templates')
file_blueprint = Blueprint('scan/file', __name__, template_folder='templates')

UPLOAD_FOLDER = 'app/mods/mod_scan/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv', 'pcap'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

###################
#### functions ####
###################

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

################
#### routes ####
################

@scan_blueprint.route('/scan', methods= ['GET', 'POST'])
def scan():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            error = "No selected file"
            return redirect("/scan", error=error)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            isolation_forest(filename)
            #fileurl = filename.split('.')
            #return redirect(url_for("/"+fileurl[0]))
            return redirect("/scan/file")
    else:
        return render_template("scan.html")

@file_blueprint.route('/scan/file', methods= ['GET', 'POST'])
def file():
    lat = ""
    lon = ""
    # Import DF from SQLite
    disk_engine = create_engine('sqlite:///app/mods/mod_scan/isolation_forest.db')
    df = pd.read_sql_query('SELECT * FROM anomalies', disk_engine)
    df2 = pd.read_sql_query('SELECT * FROM data', disk_engine)
    dfJSON = df.to_json(orient='index')

    # Anomalies MAP
    mapbox_access_token = 'pk.eyJ1IjoiYWxleGZyYW5jb3ciLCJhIjoiY2pnbHlncDF5MHU4OTJ3cGhpNjE1eTV6ZCJ9.9RoVOSpRXa2JE9j_qnELdw'
    ips = df[(df['type'] == 'public')]['ipdst'].values
    print(ips)

    outputLat = []
    outputLon = []
    for ip in ips:
        url = 'http://freegeoip.net/json/'+ip
        response = urllib.request.urlopen(url)
        str_response = response.read().decode('utf-8')
        data = json.loads(str_response)

        try:
            data['message']

        except (KeyError, TypeError) as e:
            lat = str(data['latitude'])
            latList = str(data['latitude']).split()
            lon = str(data['longitude'])
            lonList = str(data['longitude']).split()
            outputLat.append(lat)
            outputLon.append(lon)

    data = Data([
        Scattermapbox(
            lat=outputLat,
            lon=outputLon,
            mode='markers',
            name="Anomalies",
            marker=Marker(
                size=14,
                color='rgb(255, 0, 0)',
                opacity=0.7
            ),
            text=ips,
        ),
    ])

    layout = Layout(
        autosize=True,
    	height=600,
        hovermode='closest',
	margin=dict(
        	l=30,
        	r=30,
        	b=0,
        	t=0,
    	),
        showlegend=False,
	plot_bgcolor='#fffcfc',
        paper_bgcolor='#fffcfc',
	mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat,
                lon=lon
            ),
            pitch=0,
            style='dark',
            zoom=1,
        ),
        legend=dict(
            x=1,
            y=0,
            traceorder='normal',
            font=dict(
                family='sans-serif',
                size=12,
                color='#000'
            ),
            bgcolor='#E2E2E2',
            bordercolor='#FFFFFF',
            borderwidth=2
        ),
    )

    varAnomalies = df[(df['prediction'] == -1)]
    figMap = dict(data=data, layout=layout)
    graphJSON = json.dumps(figMap, cls=plotly.utils.PlotlyJSONEncoder)
    print(graphJSON)
    varAnomalies = varAnomalies[['ipdst','proto','time','count']]

    # Anomalies table
    html = varAnomalies.to_html(classes="table-dark")
    html = re.sub(
        r'<table([^>]*)>',
        r'<table\1 data-sortable>',
        html
    )

    html = html.split('\n')


    # Charts
    # Vars
        # Time order
    df3 = df2.sort_values(by=['time'])
        #Normal Traffic
    nor = df3[(df3['prediction'] == 1)]['count']
        #Anomalies
    ano = df3[(df3['prediction'] == -1)]['count']


    normal = go.Scatter(
        x = df3[(df3['prediction'] == 1)]['time'],
        y = nor,
        mode = "lines",
        name = "Normal Traffic"
    )

    anomalies = dict(
        x=df3[(df3['prediction'] == -1)]['time'],
        y=ano,
        name = "Anomalies",
        mode = 'markers',
        marker=Marker(
                size=7,
                symbol= "circle",
                color='rgb(255, 0, 0)'
            ),
        opacity = 0.8)

    data = [normal, anomalies]

    layout = dict(
        title='Peticiones totales por tiempo',
        xaxis=dict(
            #title = 'Date',
            #rangeslider=dict(),
            type='date'
        ),
        yaxis=dict(
            title = 'Nº packets'
        ),
        legend=dict(
            x=1,
            y=1,
            traceorder='normal',
            font=dict(
                family='sans-serif',
                size=12,
                color='#000'
            ),
            bgcolor='#E2E2E2',
            bordercolor='#FFFFFF',
            borderwidth=2
        )
    )

    figChart = dict(data=data, layout=layout)
    chartJSON = json.dumps(figChart, cls=plotly.utils.PlotlyJSONEncoder)
    print(chartJSON)

    # Chart2
        # Vars
    anomaliesP = df2[(df2['prediction'] == -1)]['ipdst']
    anomaliesC = df2[(df2['prediction'] == -1)]['count']

    x = list(anomaliesP)
    y = list(anomaliesC)
    print(x)
    print(y)

    labels = x
    values = y

    data = [go.Bar(
                x=x,
                y=y,
                marker=dict(
                    color='rgb(158,202,225)',
                    line=dict(
                        color='rgb(8,48,107)',
                        width=1.5,
                    )
                ),
                opacity=0.6
            )]
    layout = dict(
        title='Peticiones totales por IP',
    )

    figChart2 = dict(data=data, layout=layout)
    chartJSON2 = json.dumps(figChart2, cls=plotly.utils.PlotlyJSONEncoder)

    #return render_template('index.html', graphJSON=graphJSON, tables=[varAnomalies.to_html(classes="table sortable-theme-dark")], titles=['ipdst', 'proto'])
    return render_template('file.html', graphJSON=graphJSON, tables=html, chartJSON=chartJSON, chartJSON2=chartJSON2)


if __name__ == "__main__":
        app.run(debug=True)
