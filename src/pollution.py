import os, sys, traceback
import threading
import time
import random
from queue import Queue
from flask_restful import Resource
from util import safe_cast
from pms5003 import PMS5003


class PollutionMeasure:
    def __init__(self, pm1_0=0, pm2_5=0, pm10=0, pm1_0_atm=0, pm2_5_atm=0, pm10_atm=0, gt0_3um=0, gt0_5um=0, gt1_0um=0,
                 gt2_5um=0, gt5_0um=0, gt10um=0):
        self.pm1_0 = pm1_0
        self.pm2_5 = pm2_5
        self.pm10 = pm10
        self.pm1_0_atm = pm1_0_atm
        self.pm2_5_atm = pm2_5_atm
        self.pm10_atm = pm10_atm
        self.gt0_3um = gt0_3um
        self.gt0_5um = gt0_5um
        self.gt1_0um = gt1_0um
        self.gt2_5um = gt2_5um
        self.gt5_0um = gt5_0um
        self.gt10um = gt10um


class PollutionQueue:
    def __init__(self, max_queue_size=5, seconds_interval=1):
        self.values = Queue(maxsize=max_queue_size)
        self.seconds_interval = seconds_interval

    def read_pollution(self):
        print("read_pollution() started!")
        pms5003 = PMS5003()
        while True:
            try:
                measure = str(pms5003.read()).strip()
                lines = measure.splitlines()
                measurements = PollutionMeasure(
                    safe_cast(lines[0].rpartition(':')[2], int),
                    safe_cast(lines[1].rpartition(':')[2], int),
                    safe_cast(lines[2].rpartition(':')[2], int),
                    safe_cast(lines[3].rpartition(':')[2], int),
                    safe_cast(lines[4].rpartition(':')[2], int),
                    safe_cast(lines[5].rpartition(':')[2], int),
                    safe_cast(lines[6].rpartition(':')[2], int),
                    safe_cast(lines[7].rpartition(':')[2], int),
                    safe_cast(lines[8].rpartition(':')[2], int),
                    safe_cast(lines[9].rpartition(':')[2], int),
                    safe_cast(lines[10].rpartition(':')[2], int),
                    safe_cast(lines[11].rpartition(':')[2], int))

                if self.values.full():
                    self.values.get()
                self.values.put(measurements)

                print(f"Elementi in coda Pollution: {self.values.qsize()}")
                time.sleep(self.seconds_interval)
            except Exception as ex:
                print(ex)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(f"exception_type: {exc_type}")
                print(f"exception_value: {exc_value}")
                print(f"exception_traceback: {traceback.format_exc().splitlines()}")
                time.sleep(5)
                pms5003 = PMS5003()


    def get_mean(self):
        if self.values.empty():
            print("No elements in pollution queue")
            return None
        pm1_0_array = []
        pm2_5_array = []
        pm10_array = []
        pm1_0_atm_array = []
        pm2_5_atm_array = []
        pm10_atm_array = []
        gt0_3um_array = []
        gt0_5um_array = []
        gt1_0um_array = []
        gt2_5um_array = []
        gt5_0um_array = []
        gt10um_array = []

        for element in list(self.values.queue):
            pm1_0_array.append(element.pm1_0)
            pm2_5_array.append(element.pm2_5)
            pm10_array.append(element.pm10)
            pm1_0_atm_array.append(element.pm1_0_atm)
            pm2_5_atm_array.append(element.pm2_5_atm)
            pm10_atm_array.append(element.pm10_atm)
            gt0_3um_array.append(element.gt0_3um)
            gt0_5um_array.append(element.gt0_5um)
            gt1_0um_array.append(element.gt1_0um)
            gt2_5um_array.append(element.gt2_5um)
            gt5_0um_array.append(element.gt5_0um)
            gt10um_array.append(element.gt10um)

        return PollutionMeasure(
            safe_cast(sum(pm1_0_array) / len(pm1_0_array), int),
            safe_cast(sum(pm2_5_array) / len(pm2_5_array), int),
            safe_cast(sum(pm10_array) / len(pm10_array), int),
            safe_cast(sum(pm1_0_atm_array) / len(pm1_0_atm_array), int),
            safe_cast(sum(pm2_5_atm_array) / len(pm2_5_atm_array), int),
            safe_cast(sum(pm10_atm_array) / len(pm10_atm_array), int),
            safe_cast(sum(gt0_3um_array) / len(gt0_3um_array), int),
            safe_cast(sum(gt0_5um_array) / len(gt0_5um_array), int),
            safe_cast(sum(gt1_0um_array) / len(gt1_0um_array), int),
            safe_cast(sum(gt2_5um_array) / len(gt2_5um_array), int),
            safe_cast(sum(gt5_0um_array) / len(gt5_0um_array), int),
            safe_cast(sum(gt10um_array) / len(gt10um_array), int))


pollution_queue = PollutionQueue(max_queue_size=5, seconds_interval=3)


class PollutionResource(Resource):
    def get(self):
        try:
            return pollution_queue.get_mean().__dict__
        except Exception as ex:
            print(ex)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return {'exception_type': str(exc_type),
                    'exception_value': str(exc_value),
                    'exception_traceback': traceback.format_exc().splitlines()}


class PollutionThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.board = 1

    def run(self):
        pollution_queue.read_pollution()
