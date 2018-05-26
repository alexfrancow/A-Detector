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

# Isolation Forest
from sklearn.pipeline import Pipeline
from sklearn.ensemble import IsolationForest

# SQLite
from sqlalchemy import create_engine
import datetime as dt

################
#### CONFIG ####
################


##############
#### MAIN ####
##############

def isolation_forest(filename):
    df = pd.read_csv('app/mod_scan/uploads/'+filename)
    df.columns = ['no', 'time', 'x', 'info', 'ipsrc', 'ipdst', 'proto', 'len']
    df['info'] = "null"
    df.parse_dates=["time"]
    df['time'] = pd.to_datetime(df['time'])
    df['count'] = 1
    dataGroup2 = df.groupby(['ipdst','proto']).resample('5S', on='time').sum().reset_index().dropna()
    pd.options.display.float_format = '{:,.0f}'.format
    dataGroup2 = dataGroup2[['ipdst','proto','time','count']]
    dataNorm = dataGroup2.copy()
    dataNorm['count_n'] = (dataGroup2['count'] - dataGroup2['count'].min()) / (dataGroup2['count'].max() - dataGroup2['count'].min())
    dataNorm = dataNorm
    dataNorm = dataNorm[['count','count_n']]
    dataTrain = dataNorm.iloc[100:110000]

    iforest = IsolationForest(n_estimators=100, contamination=0.00001, max_samples=256)
    iforest.fit(dataTrain)
    clf = iforest.fit(dataTrain)
    prediction = iforest.predict(dataNorm)

    dataGroup2['prediction'] = prediction
    dataGroup2[['count','prediction']]

    # Only the ipdst is output
    anomalies = dataGroup2[(dataGroup2['prediction'] == -1)]['ipdst'].values

    disk_engine = create_engine('sqlite:///app/mod_scan/isolation_forest.db')
    dataGroup2.to_sql('data', disk_engine, if_exists='replace')
    print(anomalies)
    return "DONE"
