"""
Command:
    python3 main.py
"""

import os, sys, traceback
import pprint
import logging

from flask import Flask
from flask_restful import Resource, Api
from pms5003 import PMS5003
from enviroplus import gas


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
api = Api(app)
pms5003 = PMS5003()
gas.enable_adc()


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


class Pollution(Resource):
    def get(self):
        try:
            measure = str(pms5003.read()).strip()
            lines = measure.splitlines()
            #for l in lines:
            #    print(f" {l} ---> {safe_cast(l.rpartition(':')[2], int)} ")

            pm1_0 = safe_cast(lines[0].rpartition(':')[2], int)
            pm2_5 = safe_cast(lines[1].rpartition(':')[2], int)
            pm10 = safe_cast(lines[2].rpartition(':')[2], int)
            pm1_0_atm = safe_cast(lines[3].rpartition(':')[2], int)
            pm2_5_atm = safe_cast(lines[4].rpartition(':')[2], int)
            pm10_atm = safe_cast(lines[5].rpartition(':')[2], int)
            gt0_3um = safe_cast(lines[6].rpartition(':')[2], int)
            gt0_5um = safe_cast(lines[7].rpartition(':')[2], int)
            gt1_0um = safe_cast(lines[8].rpartition(':')[2], int)
            gt2_5um = safe_cast(lines[9].rpartition(':')[2], int)
            gt5_0um = safe_cast(lines[10].rpartition(':')[2], int)
            gt10um = safe_cast(lines[11].rpartition(':')[2], int)

            return {'pm1_0': pm1_0,
                    'pm2_5': pm2_5,
                    'pm10': pm10,
                    'pm1_0_atm': pm1_0_atm,
                    'pm2_5_atm': pm2_5_atm,
                    'pm10_atm': pm10_atm,
                    'gt0_3um': gt0_3um,
                    'gt0_5um': gt0_5um,
                    'gt1_0um': gt1_0um,
                    'gt2_5um': gt2_5um,
                    'gt5_0um': gt5_0um,
                    'gt10um': gt10um
                    }
        except Exception as ex:
            print(ex)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return {'exception_type': str(exc_type),
                    'exception_value': str(exc_value),
                    'exception_traceback': traceback.format_exc().splitlines()}


class Gas(Resource):
    def get(self):
        try:
            measurements = gas.read_all()
            #print(measurements)

            oxidising = safe_cast(measurements.oxidising, float)
            reducing = safe_cast(measurements.reducing, float)
            nh3 = safe_cast(measurements.nh3, float)
            adc = safe_cast(measurements.adc, float)

            return {'adc': adc,
                    'nh3': nh3,
                    'oxidising': oxidising,
                    'reducing': reducing
                    }
        except Exception as ex:
            print(ex)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return {'exception_type': str(exc_type),
                    'exception_value': str(exc_value),
                    'exception_traceback': traceback.format_exc().splitlines()}


api.add_resource(HelloWorld, '/', '/hello')
api.add_resource(Serial, '/serial')
api.add_resource(Pollution, '/pollution')
api.add_resource(Gas, '/gas')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
