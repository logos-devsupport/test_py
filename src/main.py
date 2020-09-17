"""

Command example:
    python3 main.py
"""

import datetime
import time
import os
import sys
import pprint as pp
import logging

#logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)-10s  %(message)s', filename=os.path.dirname(os.path.abspath(__file__))+time.strftime("\logs\crea_mappa_%Y-%m-%d.log"))

from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(HelloWorld, '/hello')

if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True)
