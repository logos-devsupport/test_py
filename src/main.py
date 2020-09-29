"""
Command:
    python3 main.py
"""

import os, sys, traceback
import pprint

from flask import Flask
from flask_restful import Resource, Api
from gas import GasThread, GasResource
from pollution import PollutionThread, PollutionResource

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Serial(Resource):
    def get(self):
        cpu_serial = "0000000000000000"
        try:
            f = open('/proc/device-tree/serial-number', 'r')
            for line in f:
                cpu_serial = line[0:16]
            f.close()
        except:
            cpu_serial = "ERROR000000000"
        return {'serial_number': cpu_serial}


api.add_resource(HelloWorld, '/', '/hello')
api.add_resource(Serial, '/serial')
api.add_resource(PollutionResource, '/pollution')
api.add_resource(GasResource, '/gas')

if __name__ == '__main__':
    print("Starting threads...")
    gas_thread = GasThread()
    pollution_thread = PollutionThread()
    gas_thread.start()
    pollution_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

