# -*- encoding: utf-8 -*-
"""
A-Detector
Licence: GPLv3
Autor: @alexfrancow
"""

#################
#### imports ####
#################

# Standard
import pandas as pd
import numpy as np
import os

# Isolation Forest
from sklearn.pipeline import Pipeline
from sklearn.ensemble import IsolationForest

# SQLite
from sqlalchemy import create_engine
import datetime as dt

################
#### CONFIG ####
################


###################
#### FUNCTIONS ####
###################

def is_public_ip(ip):
    ip = list(map(int, ip.strip().split('.')[:2]))
    if ip[0] == 10: return False
    if ip[0] == 172 and ip[1] in range(16, 32): return False
    if ip[0] == 192 and ip[1] == 168: return False
    return True

def isolation_forest(filename):
    # Convert data
    print('Converting data..')
    os.system("tshark -r app/mods/mod_scan/uploads/"+filename + " -T fields -e frame.number -e frame.time -e ip.src -e ip.dst -e _ws.col.Protocol -e _ws.col.Info -E header=y -E separator=, -E quote=d -E occurrence=f > app/mods/mod_scan/uploads/test.csv")

    # Import data
    df = pd.read_csv('app/mods/mod_scan/uploads/test.csv')
    df.columns = ['no', 'time', 'ipsrc', 'ipdst', 'proto', 'info']
    df['info'] = "null"
    df.parse_dates=["time"]
    df['time'] = pd.to_datetime(df['time'])
    df['count'] = 1

    # Group
    dataGroup2 = df.groupby(['ipdst','proto']).resample('5S', on='time').sum().reset_index().dropna()
    pd.options.display.float_format = '{:,.0f}'.format
    dataGroup2 = dataGroup2[['ipdst','proto','time','count']]

    # Normalize
    dataNorm = dataGroup2.copy()
    dataNorm['count_n'] = (dataGroup2['count'] - dataGroup2['count'].min()) / (dataGroup2['count'].max() - dataGroup2['count'].min())
    dataNorm = dataNorm
    dataNorm = dataNorm[['count','count_n']]

    # Isolation Forest
    dataTrain = dataNorm.iloc[0:1000]
    iforest = IsolationForest(n_estimators=100, contamination=0.00001, max_samples=256)
    iforest.fit(dataTrain)
    clf = iforest.fit(dataTrain)
    prediction = iforest.predict(dataNorm)
    dataGroup2['prediction'] = prediction

    # Save the anomalies in a new var
    dataGroup3 = dataGroup2[(dataGroup2['prediction'] == -1)]

    # Save the anomalies ipdst in a new var
    anomalies = dataGroup2[(dataGroup2['prediction'] == -1)]['ipdst'].values

    # Check anomalies IP type
    ips = anomalies
    type = []
    for ip in ips:
        if is_public_ip(ip):
            type.append('public')
        else:
            type.append('private')
    dataGroup3['type'] = type

    disk_engine = create_engine('sqlite:///app/mods/mod_scan/isolation_forest.db')

    # Save all data included anomalies in a new table
    dataGroup2.to_sql('data', disk_engine, if_exists='replace')

    # Save anomalies + IP type in a new table
    dataGroup3.to_sql('anomalies', disk_engine, if_exists='replace')
    return "DONE"
