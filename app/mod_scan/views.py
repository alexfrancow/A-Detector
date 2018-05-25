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

from app.mod_scan.isolation_forest import isolation_forest

################
#### config ####
################

scan_blueprint = Blueprint('scan', __name__, template_folder='templates')

UPLOAD_FOLDER = 'app/mod_scan/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

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
            return redirect("/anomalies")
    else:
        return render_template("scan.html")

if __name__ == "__main__":
        app.run(debug=True)
