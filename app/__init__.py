# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""

#################
#### imports ####
#################

from flask import Flask

################
#### config ####
################

from config import *
app = Flask(__name__, instance_relative_config=True)

####################
#### blueprints ####
####################

from app.mods.mod_anomalies.views import anomalies_blueprint
from app.mods.mod_dynamic.views import dynamic_blueprint
from app.mods.mod_scan.views import scan_blueprint
from app.mods.mod_scan.views import file_blueprint
from app.mods.mod_config.views import config_blueprint

# register the blueprints
app.register_blueprint(anomalies_blueprint)
app.register_blueprint(dynamic_blueprint)
app.register_blueprint(scan_blueprint)
app.register_blueprint(file_blueprint)
app.register_blueprint(config_blueprint)

@app.context_processor
def inject_dict_for_all_templates():
    print(LOCAL_IP)
    return dict(LOCAL_IP=LOCAL_IP, IF_CONTAMINATION=IF_CONTAMINATION)
