from flask import Blueprint, render_template

from flask import Flask, render_template
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

disk_engine = create_engine('sqlite:///test.db')
df = pd.read_sql_query('SELECT * FROM data', disk_engine)
df2 = pd.read_sql_query('SELECT * FROM data', disk_engine)
dfJSON = df.to_json(orient='index')


anomalies_blueprint = Blueprint('anomalies', __name__, template_folder='templates')

app = Flask(__name__)

@anomalies_blueprint.route('/anomalies')
def anomalies():
    mapbox_access_token = 'pk.eyJ1IjoiYWxleGZyYW5jb3ciLCJhIjoiY2pnbHlncDF5MHU4OTJ3cGhpNjE1eTV6ZCJ9.9RoVOSpRXa2JE9j_qnELdw'
    #ips = ['157.240.21.35','23.253.135.79','104.244.42.193', '213.60.47.49']
    ips = ['92.53.104.78']

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
        	b=40,
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
    fig = dict(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print(graphJSON)
    varAnomalies = varAnomalies[['ipdst','proto','time','count']]


    html = varAnomalies.to_html(classes="table-dark")
    html = re.sub(
        r'<table([^>]*)>',
        r'<table\1 data-sortable>',
        html
    )

    html = html.split('\n')


    # Chart
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
            x=0,
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


    # Chart 2
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
            title = 'Peticiones totales',
    )

    figChart2 = dict(data=data, layout=layout)
    chartJSON2 = json.dumps(figChart2, cls=plotly.utils.PlotlyJSONEncoder)

    #return render_template('index.html', graphJSON=graphJSON, tables=[varAnomalies.to_html(classes="table sortable-theme-dark")], titles=['ipdst', 'proto'])
    return render_template('index.html', graphJSON=graphJSON, tables=html, chartJSON=chartJSON, chartJSON2=chartJSON2)

if __name__ == '__main__':
    app.run(debug= True)


