import cv2

class VideoOverlay:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            raise ValueError("Could not open motivational video")

    def overlay(self, frame):
        ret, vid = self.cap.read()

        # Restart video if it ends
        if not ret or vid is None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, vid = self.cap.read()
            if not ret:
                return frame   # fail safely

        h, w, _ = frame.shape

        # Resize safely
        vid = cv2.resize(vid, (int(w * 0.25), int(h * 0.25)))

        vh, vw, _ = vid.shape

        # Top-right placement
        frame[10:10+vh, w-vw-10:w-10] = vid
        return frame
