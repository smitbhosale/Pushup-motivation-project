import cv2
import mediapipe as mp
import numpy as np
import time

mp_pose = mp.solutions.pose

class PushUpCounter:
    def __init__(self):
        self.pose = mp_pose.Pose()
        self.count = 0
        self.stage = "up"
        self.last_count_time = 0

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
                  np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = abs(radians * 180.0 / np.pi)
        return angle if angle <= 180 else 360 - angle

    def process(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)

        if not results.pose_landmarks:
            return False

        lm = results.pose_landmarks.landmark

        shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        angle = self.calculate_angle(shoulder, elbow, wrist)

        now = time.time()

        if angle > 160:
            self.stage = "up"

        if angle < 90 and self.stage == "up":
            if now - self.last_count_time > 0.7:
                self.count += 1
                self.stage = "down"
                self.last_count_time = now
                return True

        return False
