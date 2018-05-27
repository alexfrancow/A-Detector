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

app = Flask(__name__, instance_relative_config=True)

####################
#### blueprints ####
####################

from app.views import anomalies_blueprint
from app.mod_dynamic.views import dynamic_blueprint
from app.mod_scan.views import scan_blueprint
from app.mod_scan.views import file_blueprint
from app.mod_about.views import about_blueprint

# register the blueprints
app.register_blueprint(anomalies_blueprint)
app.register_blueprint(dynamic_blueprint)
app.register_blueprint(scan_blueprint)
app.register_blueprint(file_blueprint)
app.register_blueprint(about_blueprint)
