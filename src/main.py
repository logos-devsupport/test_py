"""
Command:
    python3 main.py
"""

import os, sys, traceback
import pprint
import logging

from flask import Flask
from flask_restful import Resource, Api
import importlib
#importlib.import_module(gas)
from gas import GasThread, GasResource
from pollution import PollutionThread, PollutionResource

# from pms5003 import PMS5003
# from enviroplus import gas





app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
api = Api(app)


# pms5003 = PMS5003()
# gas.enable_adc()


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
    print("Starting main...")
    gas_thread = GasThread()
    pollution_thread = PollutionThread()
    gas_thread.start()
    pollution_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

