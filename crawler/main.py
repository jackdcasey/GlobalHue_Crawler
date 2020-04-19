from classes.City import City
from classes.PhotoSource import PhotoSource
from classes.ImageProcessing import processPhotoSourceList, ColorLookupError
from classes.db import WriteToDatabase

from typing import List
from datetime import timedelta

import jsonpickle, schedule

import os, time, datetime, uuid

DB_TABLE_CURRENT = 'GlobalHue_Current'
DB_TABLE_HISTORY = 'GlobalHue_History'

HISTORY_DAYS = 14

INTERVAL_MIN = 15

def main():

    start()

    schedule.every(INTERVAL_MIN).minutes.do(start)

    while True:
        schedule.run_pending()
        time.sleep(1)

def start():

    print("Starting")

    cwd = os.path.dirname(os.path.abspath(__file__))
    citiesFile = os.path.join(cwd, 'cities.json')

    print(f"Loading from {citiesFile}")

    cities = loadConfig(citiesFile)

    runtime = datetime.datetime.utcnow()
    displaytime = runtime.replace(tzinfo=datetime.timezone.utc).replace(microsecond=0).isoformat()
    ttl = int((runtime + timedelta(days = HISTORY_DAYS)).timestamp())

    for city in cities:

        print(city.Name)

        success = True

        try:
            color = processPhotoSourceList(city.PhotoSourceList)
        except ColorLookupError as e:
            print(e)
            success = False
            color = "#ffffff"

        WriteToDatabase(
            DB_TABLE_CURRENT,
            {
                'city': city.Name,
                'color': color,
                'success': success,
                'capturetime': displaytime
            }
        )

        WriteToDatabase(
            DB_TABLE_HISTORY,
            {
                'uuid': str(uuid.uuid4()),
                'city': city.Name,
                'color': color,
                'success': success,
                'capturetime': displaytime,
                'ttl': ttl
            }
        )

    print("Exiting")

def loadConfig(filePath) -> List[City]:
    with open(filePath, 'r') as f:
        return jsonpickle.decode(f.read())


if __name__ == '__main__':
    main()