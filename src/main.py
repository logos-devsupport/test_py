"""
Command:
    python3 main.py
"""

import os, sys, traceback
import pprint
import logging

import threading
import time
from queue import Queue
import random

from flask import Flask
from flask_restful import Resource, Api


from pms5003 import PMS5003
from enviroplus import gas


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


class GasMeasure:
    oxidising = 0.0
    reducing = 0.0
    nh3 = 0.0
    adc = 0.0

    def __init__(self, oxidising, reducing, nh3, adc):
        self.oxidising = oxidising
        self.reducing = reducing
        self.nh3 = nh3
        self.adc = adc


class GasQueue:
    def __init__(self, max_queue_size=5, seconds_interval=1):
        self.values = Queue(maxsize=max_queue_size)
        self.seconds_interval = seconds_interval
        #print("Instanced Gas obj ", self)

    def read_gas(self):
        print("read_gas() started")
        try:
            while True:
                measurements = gas.read_all()
                #measurements = GasMeasure(1.5 * random.uniform(1, 10), 4 * random.uniform(1, 10), 12.3 * random.uniform(1, 10), 3.8 * random.uniform(1, 10))
                if self.values.full():
                    self.values.get()
                self.values.put(
                    GasMeasure(measurements.oxidising, measurements.reducing, measurements.nh3, measurements.adc))

                #pprint.pprint(f"Elementi in coda: {self.values.qsize()}")
                #pprint.pprint(self.values.queue)
                time.sleep(self.seconds_interval)
        except:
            print("Exception in read_gas()!")
            raise

    def get_mean(self):
        if self.values.empty():
            return None
        oxidising_array = []
        reducing_array = []
        nh3_array = []
        adc_array = []
        for element in list(self.values.queue):
            oxidising_array.append(element.oxidising)
            reducing_array.append(element.reducing)
            nh3_array.append(element.nh3)
            adc_array.append(element.adc)

        return GasMeasure(sum(oxidising_array)/len(oxidising_array),
                          sum(reducing_array)/len(reducing_array),
                          sum(nh3_array)/len(nh3_array),
                          sum(adc_array)/len(adc_array))


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
api = Api(app)
gas_queue = GasQueue(max_queue_size=5, seconds_interval=1)


class GasThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.board = 1

    def run(self):
        gas_queue.read_gas()


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
            # measure = str(pms5003.read()).strip()
            measure = """PM1.0 ug/m3 (ultrafine particles):                             2
            #PM2.5 ug/m3 (combustion particles, organic compounds, metals): 3
            #PM10 ug/m3  (dust, pollen, mould spores):                      4
            #PM1.0 ug/m3 (atmos env):                                       2
            #PM2.5 ug/m3 (atmos env):                                       3
            #PM10 ug/m3 (atmos env):                                        4
            #>0.3um in 0.1L air:                                            663
            #>0.5um in 0.1L air:                                            168
            #>1.0um in 0.1L air:                                            24
            #>2.5um in 0.1L air:                                            2
            #>5.0um in 0.1L air:                                            0
            #>10um in 0.1L air:                                             0
            #"""
            lines = measure.splitlines()
            # for l in lines:
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
            #global gas_queue
            # measurements = gas.read_all()
            measurements = gas_queue.get_mean()
            # print(measurements)

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
    print("Starting main...")
    gas_thread = GasThread()
    gas_thread.start()

    #gas_thread = threading.Thread(target=gas_queue.read_gas(), args=())
    #gas_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
    #server_thread = threading.Thread(target=app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False), args=())
    #threading.Thread(target=app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False, threaded=True)).start()
    #server_thread.start()

    #gas_queue.read_gas()

    #threading.Thread(target=gas_queue.read_gas()).start()
    #gas_thread.start()
