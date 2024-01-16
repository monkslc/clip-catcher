import cv2
import time
from datetime import datetime

from lib.clip import Clipper
from lib.loudness import LoudnessDetector

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    clipper = Clipper(cap, 2000)

    loudness_detector = LoudnessDetector(2500, buffer_ms=2000)

    while True:
        try:
            msg = loudness_detector.out_queue.get()
            time.sleep(1)
            clipper.clip(2000, "swing-" + datetime.now().strftime("%y-%m-%d-%H%M%S") + ".mp4")

        except KeyboardInterrupt:
            clipper.stop()
            loudness_detector.stop()
            cv2.destroyAllWindows()
            break