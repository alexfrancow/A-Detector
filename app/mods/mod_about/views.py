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

about_blueprint = Blueprint('about', __name__, template_folder='templates')

app = Flask(__name__)

###################
#### functions ####
###################


################
#### routes ####
################

@about_blueprint.route('/about', methods= ['GET'])
def about():
    return render_template("about.html")

if __name__ == "__main__":
        app.run(debug=True)
