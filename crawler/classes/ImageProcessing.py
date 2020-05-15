from classes.PhotoSource import PhotoSource

from typing import List

from cv2 import cv2
import numpy as np
import requests, ffmpeg

import os, logging

def processPhotoSourceList(sourcelist: List[PhotoSource]) -> str:

    colors = []

    for source in sourcelist:

        try:
            imageArr = getImageArrayFromUrl(source.Url, source.Kind)
            imageArrCrop = cropImageArray(imageArr, source.CropTop, source.CropBottom, source.CropLeft, source.CropRight)
            color = getAverageColor(imageArrCrop)
            colors.append(color)
        except:
            logging.error(f"Error loading color from: {source.Url}")

    if len(colors) == 0:
        raise ColorLookupError("Unable to determine color from all sources")

    avg = np.mean(colors, axis = 0)

    return getColorString(avg)


def cropImageArray(img: np.ndarray, cropTop: int, cropBottom: int, cropLeft: int, cropRight: int) -> np.ndarray:

    h = img.shape[0]
    w = img.shape[0]

    ct = int(h * (cropTop / 100))
    cb = int(h - (h * (cropBottom / 100)))

    cl = int(w * (cropLeft / 100))
    cr = int(w - (w * (cropRight / 100)))

    return img[ct:cb, cl:cr]

def getAverageColor(img: np.ndarray) -> str:

    img = cv2.resize(img, (150, 150))

    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    dominant = palette[np.argmax(counts)]

    return dominant


def getImageArrayFromFile(filename: str) -> np.ndarray:

    if not os.path.exists(filename): raise FileNotFoundError

    return cv2.imread(filename)

def getImageArrayFromUrl(url: str, kind: str) -> np.ndarray:

    logging.info(f"Opening {url} as {kind}")

    if kind == "Image":

        resp = requests.get(url)
        image = np.asarray(bytearray(resp.content), dtype="uint8")

        return cv2.imdecode(image, -1)

    if kind == "Stream":

        out, _ = (
            ffmpeg
            .input(url)
            .output('pipe:', format='image2', vcodec='mjpeg', vframes=1)
            .global_args('-loglevel', 'warning')
            .global_args('-hide_banner')
            .run(capture_stdout=True)
        )

        image = np.asarray(bytearray(out) ,dtype=np.uint8)

        return cv2.imdecode(image, -1)

def getColorString(color: np.ndarray) -> str:

    colorHex = [format(int(c), 'x').zfill(2) for c in color]
    colorStr = f"#{''.join(colorHex[::-1])}"

    return colorStr

class ColorLookupError(Exception):

    def __init__(self, message):
        super().__init__(message)