from classes.City import City
from classes.PhotoSource import PhotoSource
from classes.ImageProcessing import processPhotoSourceList, ColorLookupError
from classes.db import WriteToDatabase
from classes.s3 import getFileFromS3

from typing import List
from datetime import timedelta

import jsonpickle, schedule

import os, time, datetime, uuid, logging

DB_TABLE_CURRENT = 'GlobalHue_Current'
DB_TABLE_HISTORY = 'GlobalHue_History'

CONFIG_BUCKET = 'globalhue-configs'

HISTORY_DAYS = 14

INTERVAL_MIN = 15

logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level = logging.INFO
)

def main():

    start()

    schedule.every(INTERVAL_MIN).minutes.do(start)

    while True:
        schedule.run_pending()
        time.sleep(1)

def start():

    logging.info("Starting")

    cities = loadConfig('cities.json')

    runtime = datetime.datetime.utcnow()
    displaytime = runtime.replace(tzinfo=datetime.timezone.utc).replace(microsecond=0).isoformat()
    ttl = int((runtime + timedelta(days = HISTORY_DAYS)).timestamp())

    for city in cities:

        logging.info(city.Name)

        success = True

        try:
            color = processPhotoSourceList(city.PhotoSourceList)
        except ColorLookupError as e:
            logging.error(e)
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

    logging.info("Completed")

def loadConfig(filename) -> List[City]:

    rawconfig = getFileFromS3(CONFIG_BUCKET, filename)
    return jsonpickle.decode(rawconfig)


if __name__ == '__main__':
    main()