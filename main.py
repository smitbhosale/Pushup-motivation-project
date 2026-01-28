import cv2
import time

from pushup_counter import PushUpCounter
from video_overlay import VideoOverlay
from audio_player import AudioPlayer
from config import INACTIVITY_TIME, VIDEO_PATH, AUDIO_PATH, DEFAULT_PUSHUP_LIMIT

# -------------------------------
# Ask user for push-up target
# -------------------------------
try:
    PUSHUP_LIMIT = int(input("Enter your push-up target: "))
    if PUSHUP_LIMIT <= 0:
        raise ValueError
except ValueError:
    print("Invalid input. Using default target.")
    PUSHUP_LIMIT = DEFAULT_PUSHUP_LIMIT

# -------------------------------
# Initialize components
# -------------------------------
cap = cv2.VideoCapture(0)

counter = PushUpCounter()
video = VideoOverlay(VIDEO_PATH)
audio = AudioPlayer(AUDIO_PATH)

last_pushup_time = time.time()

# -------------------------------
# Main loop
# -------------------------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Mirror view for better UX
    frame = cv2.flip(frame, 1)

    # Process push-up
    did_pushup = counter.process(frame)
    if did_pushup:
        last_pushup_time = time.time()

    # -------------------------------
    # Draw push-up counter
    # -------------------------------
    cv2.putText(
        frame,
        f"Push-ups: {counter.count}/{PUSHUP_LIMIT}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # -------------------------------
    # Inactivity logic
    # -------------------------------
    if time.time() - last_pushup_time > INACTIVITY_TIME:
        frame = video.overlay(frame)
        audio.play()

        cv2.putText(
            frame,
            "PUSH PUSH PUSH",
            (50, frame.shape[0] - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 0, 255),
            3
        )
    else:
        audio.stop()

    # -------------------------------
    # Target achieved
    # -------------------------------
    if counter.count >= PUSHUP_LIMIT:
        audio.stop()
        cv2.putText(
            frame,
            "TARGET ACHIEVED!",
            (200, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 215, 255),
            4
        )
        cv2.imshow("Push-up Motivation System", frame)
        cv2.waitKey(3000)
        break

    # -------------------------------
    # Show frame (ALWAYS)
    # -------------------------------
    cv2.imshow("Push-up Motivation System", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# -------------------------------
# Cleanup
# -------------------------------
cap.release()
cv2.destroyAllWindows()
