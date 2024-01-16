import pyaudio
import threading
from queue import Queue, Empty
import numpy as np
import time

FRAMES_PER_BUFFER=1024

class LoudnessDetector:
    """
    A class for detecting loud sounds

    The class detects loud sounds using the default audio device for the system. Audio is processed in
    buffers of 1024 frames. Loudness is determined by comparing the mean value of the amplitudes for
    the buffer to a threshold that is passed in the constructor. When a loud sound is detected a message
    sent to the out_queue Queue of the class containing the mean amplitude value for the buffer that
    triggered the threshold.

    Attributes
    ----------
    out_queue : queue.Queue
        Queue that is written to when a loud sound is detected
    """
    def __init__(self, threshold, buffer_ms=0):
        """
        Initializes a LoudnessDetector instance

        Parameters
        ----------
        threshold : int
            Threshold to determine if a buffer was "loud". Compared to the mean value of amplitudes for a buffer.
        buffer_ms : int
            Delay to add after detecting a loud sound before listening for loud sounds again. Used to avoid firing off multiple events for the same sound.

        """
        self._p = pyaudio.PyAudio()
        self._stream = self._p.open(format=pyaudio.paInt16,
                        channels=1,
                        # Common sampling frequency that seems to work for our application: https://en.wikipedia.org/wiki/44,100_Hz
                        rate=44100,
                        input=True,
                        frames_per_buffer=FRAMES_PER_BUFFER
                    )

        self._threshold = threshold
        self._buffer_ms = buffer_ms
        self._in_queue = Queue()
        self.out_queue = Queue()

        t = threading.Thread(target=self._start)
        self._thread = t
        self._thread.start()
        self._active = True

    def stop(self):
        """
        Stop the LoudnessDetector

        Cleans up resources.

        If the LoudnessDetector is not active, the function returns immediately
        """
        if not self._active:
            return

        self._active = False
        self._in_queue.put("stop")
        self._thread.join()
        self._stream.stop_stream()
        self._stream.close()
        self._p.terminate()


    def _start(self):
        while True:
            data = self._stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.int16)
            mean = np.mean(np.abs(audio_array))

            if mean > self._threshold:
                print("Detected loud sound")
                self.out_queue.put(mean, False)
                time.sleep(self._buffer_ms / 1000)

            try:
                msg = self._in_queue.get(False)
                if msg == "stop":
                    break

                raise Exception("Unknown message type")
            except Empty:
                continue