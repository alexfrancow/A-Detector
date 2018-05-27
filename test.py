import pandas as pd
from sqlalchemy import create_engine
import datetime as dt

disk_engine = create_engine('sqlite:///app/mod_scan/isolation_forest.db')
df = pd.read_sql_query('SELECT * FROM data', disk_engine)
df

df = df[(df['prediction'] == -1)]
anomalies = df[(df['prediction'] == -1)]['ipdst'].values
df

def public(ip):
    ip = list(map(int, ip.strip().split('.')[:2]))
    if ip[0] == 10: return False
    if ip[0] == 172 and ip[1] in range(16, 32): return False
    if ip[0] == 192 and ip[1] == 168: return False
    return True

ips = anomalies
type = []
for ip in ips:
    if public(ip):
        type.append('private')
    else:
        type.append('public')

df['type'] = type
df
