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

################
#### config ####
################

config_blueprint = Blueprint('config', __name__, template_folder='templates')

app = Flask(__name__)

###################
#### functions ####
###################


################
#### routes ####
################

@config_blueprint.route('/config', methods= ['GET', 'POST'])
def config():
    if request.method == 'POST':
        local_ip_config = request.form['local_ip']
        if_contamination_config = request.form['if_contamination']
        with open('config.py', 'w') as file:
            file.write("LOCAL_IP = '%s'\n" %local_ip_config)
            file.write("IF_CONTAMINATION = '%s'" %if_contamination_config)

        return render_template('config.html')

    else:
    #return render_template('index.html', graphJSON=graphJSON, tables=[varAnomalies.to_html(classes="table sortable-theme-dark")], titles=['ipdst', 'proto'])
    	return render_template('config.html')


if __name__ == "__main__":
        app.run(debug=True)
