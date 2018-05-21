# -*- encoding: utf-8 -*-
"""
A-Detector
Licence: GPLv3
Autor: @alexfrancow
"""

#################
#### imports ####
#################

import psutil
from flask import jsonify, Blueprint

################
#### config ####
################

dynamic_blueprint = Blueprint('dynamic', __name__, template_folder='templates')

################
#### routes ####
################

@dynamic_blueprint.route('/_stuff', methods= ['GET'])
def stuff():
    cpu=psutil.cpu_stats()
    return jsonify(cpu=cpu)

if __name__ == "__main__":
        app.run(debug=True)
