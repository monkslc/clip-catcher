import cv2
import threading
import os
from queue import Queue, Empty
from lib.ringbuffer import RingBuffer
from sys import platform

class Clipper:
    """
    A class for capturing short clips from a video stream and saving them as an mp4 file

    Initialize the class with a cv2.VideoCapture to use for the clips.
    Use `clip` to save a clip to an mp4 file.
    When the clipping is no longer needed, call `stop` to release resources.
    The class will release the cv2.VideoCapture object passed into the constructor
    """
    def __init__(self, video_capture, buffer_size=240*60, estimated_fps=30):
        """
        Initializes a Clipper instance.

        Parameters
        ----------
        video_capture : cv2.VideoCapture
            The video capture object
        buffer_size : int, optional
            Max number of frames Clipper can hold. Defaults to 240fps * 60secs.
        estimated_fps : int, optional
            The estimated frames per second. Defaults to 30
        """
        self._video_capture = video_capture
        self._msg_queue = Queue()
        self._thread = None
        self._estimated_fps = estimated_fps

        # TODO: initialize with black frames. Using None for now because I'm lazy
        self._frame_buffer = RingBuffer(buffer_size, None)
        self._ms_per_frame = (1 / estimated_fps) * 1000

        t = threading.Thread(target=self._start)
        self._thread = t
        t.start()

    def clip(self, length_ms, file_name):
        """
        Save a video clip as an mp4 file

        Makes a best attempt to make clip length length_ms based on the estimated fps passed in the
        constructor but it won't be exact. The current time is the end of the clip and the current
        time - length_ms is the start.

        If the Clipper is not active then an exception is raised.

        Parameters
        ----------
        length_ms : int
            The duration of the clip in milliseconds.
        file_name : str
            The name of the file to save the clip.
        """
        if not self.is_active():
            raise Exception("Clipper is not active")
        self._msg_queue.put(_ClipMessage(length_ms, file_name))

    def stop(self):
        """
        Stop the Clipper

        Cleans up resources.

        If the the Clipper is not active then the function returns immediately.
        """
        if not self.is_active():
            return

        self._msg_queue.put(_StopMessage())
        self._thread.join()
        self._video_capture.release()

    def is_active(self):
        """
        Check if the Clipper is currently listening for 

        Returns
        -------
        bool
            True if the Clipper is active, False otherwise.
        """
        return self._thread is not None

    def _start(self):
        """
        The main function for the worker thread.
        Continuously captures frames, processes messages, and saves clips as requested.
        """
        while True:
            ret, frame = self._video_capture.read()
            if not ret:
                # Not too sure what to do in this case other than log and continue
                print("Unable to capture video frame")
                continue

            self._frame_buffer.add(frame)
            try:
                msg = self._msg_queue.get(False)
                if msg.kind == _StopMessage.kind:
                    break

                if msg.kind == _ClipMessage.kind:
                    self._save_clip(msg.length_ms, msg.file_name)
                    continue

                raise Exception("Unknown message type")
            except Empty:
                continue

    def _save_clip(self, length_ms, file):
        """
        Private method for saving a video clip to the specified file.
        """
        num_frames = min(round(length_ms / self._ms_per_frame), len(self._frame_buffer))
        start_frame = len(self._frame_buffer) - num_frames

        width = self._video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self._video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(file, fourcc, self._estimated_fps, (int(width), int(height)))

        for i in range(start_frame, len(self._frame_buffer)):
            out.write(self._frame_buffer.get(i))

        out.release()
        print("Saved clip to", file)
        if platform == "darwin":
            os.system(f"open {file}")

class _ClipMessage:
    """
    A message class used to communicate clip requests to the Clipper.

    Don't call from outside the Clipper class. Use the `clip` method instead.
    """
    kind = "clip"
    def __init__(self, length_ms, file_name):
        self.length_ms = length_ms
        self.file_name = file_name

class _StopMessage:
    """
    A message class used to communicate a stop request to the Clipper.

    Don't call from outside the Clipper class. Use the `stop` method instead. 
    """
    kind = "stop"