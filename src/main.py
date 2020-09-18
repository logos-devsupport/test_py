"""

Command example:
    python3 main.py
"""

import os
import enviroplus
import pprint
import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)-10s  %(message)s', filename=os.path.dirname(os.path.abspath(__file__))+time.strftime("\logs\crea_mappa_%Y-%m-%d.log"))

from flask import Flask
from flask_restful import Resource, Api
from pms5003 import PMS5003


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Serial(Resource):
    def get(self):
        serial = '1234567890'
        return {'serial_number': serial}


class Pollution(Resource):
    def get(self):
        measure = """PM1.0 ug/m3 (ultrafine particles):    ,                         2.
PM2.5 ug/m3 (combustion particles, organic compounds, metals): 3
PM10 ug/m3  (dust, pollen, mould spores):                      4
PM1.0 ug/m3 (atmos env):                                       2
PM2.5 ug/m3 (atmos env):                                       3
PM10 ug/m3 (atmos env):                                        4
>0.3um in 0.1L air:                                            663
>0.5um in 0.1L air:                                            168
>1.0um in 0.1L air:                                            24
>2.5um in 0.1L air:                                            2
>5.0um in 0.1L air:                                            0
>10um in 0.1L air:                                             0
"""
        try:
            pms5003 = PMS5003()
            measure = pms5003.read()
        except Exception as ex:
            print(ex)
        lines = measure.splitlines()
        # pprint.pprint(lines)
        for l in lines:
            print(f" {l} ---> {safe_cast(l.rpartition(':')[2], int)} ")
        pm1_0 = safe_cast(lines[0].rpartition(':')[2], int)
        pm2_5 = int(lines[1].rpartition(':')[2])
        pm10 = int(lines[2].rpartition(':')[2])
        pm1_0_atm = int(lines[3].rpartition(':')[2])
        pm2_5_atm = int(lines[4].rpartition(':')[2])
        pm10_atm = int(lines[5].rpartition(':')[2])
        gt0_3um = int(lines[6].rpartition(':')[2])
        gt0_5um = int(lines[7].rpartition(':')[2])
        gt1_0um = int(lines[8].rpartition(':')[2])
        gt2_5um = int(lines[9].rpartition(':')[2])
        gt5_0um = int(lines[10].rpartition(':')[2])
        gt10um = int(lines[11].rpartition(':')[2])

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


class Gas(Resource):
    def get(self):
        measurements = ""
        # recupero valori misurati
        return {'adc': 3.5,
                'nh3': 3.5,
                'oxidising': 3.5,
                'reducing': 3.5}


api.add_resource(HelloWorld, '/', '/hello')
api.add_resource(Serial, '/serial')
api.add_resource(Pollution, '/pollution')
api.add_resource(Gas, '/gas')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

