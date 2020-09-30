import os, sys, traceback
import threading
import time
import random
from queue import Queue
from flask_restful import Resource
from enviroplus import gas
gas.enable_adc()


class GasMeasure:
    def __init__(self, oxidising=0.0, reducing=0.0, nh3=0.0, adc=0.0):
        self.adc = adc
        self.nh3 = nh3
        self.oxidising = oxidising
        self.reducing = reducing


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
                if self.values.full():
                    self.values.get()
                self.values.put(
                    GasMeasure(measurements.oxidising, measurements.reducing, measurements.nh3, measurements.adc))

                #print(f"Elementi in coda: {self.values.qsize()}")
                #print(self.values.queue)
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


gas_queue = GasQueue(max_queue_size=5, seconds_interval=1)


class GasResource(Resource):
    def get(self):
        try:
            return gas_queue.get_mean().__dict__
        except Exception as ex:
            print(ex)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return {'exception_type': str(exc_type),
                    'exception_value': str(exc_value),
                    'exception_traceback': traceback.format_exc().splitlines()}


class GasThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.board = 1

    def run(self):
        gas_queue.read_gas()

