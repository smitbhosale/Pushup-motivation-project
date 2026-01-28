import cv2
import time
import tkinter as tk
from tkinter import simpledialog


from pushup_counter import PushUpCounter
from video_overlay import VideoOverlay
from audio_player import AudioPlayer
from config import INACTIVITY_TIME, VIDEO_PATH, AUDIO_PATH, DEFAULT_PUSHUP_LIMIT

def select_motivation_media(default_video, default_audio):

    import tkinter as tk
    from tkinter import filedialog

    result = {
        "video": default_video,
        "audio": default_audio
    }

    def use_default():
        result["video"] = default_video
        result["audio"] = default_audio
        root.destroy()

    def choose_custom():
        video_path = filedialog.askopenfilename(
            title="Select Motivation Video",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")]
        )

        if video_path:
            try:
                extracted_audio = extract_audio_from_video(video_path)
                result["video"] = video_path
                result["audio"] = extracted_audio
            except Exception as e:
                print("Audio extraction failed:", e)

        root.destroy()

    root = tk.Tk()
    root.title("Motivation Media Selection")

    root.geometry("400x180")
    root.configure(bg="#1e1e1e")
    root.resizable(False, False)

    title = tk.Label(
        root,
        text="CHOOSE MOTIVATION VIDEO",
        font=("Arial", 13, "bold"),
        fg="white",
        bg="#1e1e1e"
    )
    title.pack(pady=15)

    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(pady=10)

    default_btn = tk.Button(
        btn_frame,
        text="Use Default Video",
        width=18,
        bg="#00c853",
        font=("Arial", 10, "bold"),
        command=use_default
    )
    default_btn.grid(row=0, column=0, padx=10)

    custom_btn = tk.Button(
        btn_frame,
        text="Choose Custom Video",
        width=18,
        bg="#ffab00",
        font=("Arial", 10, "bold"),
        command=choose_custom
    )
    custom_btn.grid(row=0, column=1, padx=10)

    root.mainloop()

    return result["video"], result["audio"]

def extract_audio_from_video(video_path, output_audio="temp_audio.mp3"):

    from moviepy.editor import VideoFileClip

    clip = VideoFileClip(video_path)

    if clip.audio is None:
        raise ValueError("Selected video has no audio track")

    clip.audio.write_audiofile(output_audio, verbose=False, logger=None)

    clip.close()

    return output_audio

# -------------------------------
# Ask user for push-up target
# -------------------------------
# ------------------------------------------------------------->THIS WAS OLD SIMPLE AND UGLY UI
# def get_pushup_target(default_value):
#     root = tk.Tk()
#     root.withdraw()  # Hide main window

#     target = simpledialog.askinteger(
#         title="Push-up Target",
#         prompt="Enter your push-up target:",
#         initialvalue=default_value,
#         minvalue=1
#     )

#     root.destroy()

#     if target is None:
#         return default_value

#     return target 

def get_pushup_target(default_value):

    import tkinter as tk

    result = {"value": default_value}

    def submit():
        try:
            val = int(entry.get())
            if val > 0:
                result["value"] = val
                root.destroy()
        except:
            error_label.config(text="Enter a valid positive number")

    def cancel():
        root.destroy()

    root = tk.Tk()
    root.title("Push-up Target Setup")

    # Window size
    width = 350
    height = 180

    # Center window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry(f"{width}x{height}+{x}+{y}")
    root.resizable(False, False)

    # Styling
    root.configure(bg="#1e1e1e")

    title_label = tk.Label(
        root,
        text="SET PUSH-UP TARGET",
        font=("Arial", 14, "bold"),
        fg="white",
        bg="#1e1e1e"
    )
    title_label.pack(pady=10)

    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack()

    tk.Label(
        frame,
        text="Enter target:",
        font=("Arial", 11),
        fg="white",
        bg="#1e1e1e"
    ).grid(row=0, column=0, padx=5)

    entry = tk.Entry(frame, font=("Arial", 12), width=10, justify="center")
    entry.insert(0, str(default_value))
    entry.grid(row=0, column=1, padx=5)

    error_label = tk.Label(
        root,
        text="",
        fg="red",
        bg="#1e1e1e",
        font=("Arial", 9)
    )
    error_label.pack()

    button_frame = tk.Frame(root, bg="#1e1e1e")
    button_frame.pack(pady=15)

    start_btn = tk.Button(
        button_frame,
        text="START",
        width=10,
        bg="#00c853",
        fg="black",
        font=("Arial", 10, "bold"),
        command=submit
    )
    start_btn.grid(row=0, column=0, padx=10)

    cancel_btn = tk.Button(
        button_frame,
        text="CANCEL",
        width=10,
        bg="#ff5252",
        fg="black",
        font=("Arial", 10, "bold"),
        command=cancel
    )
    cancel_btn.grid(row=0, column=1, padx=10)

    # Press Enter to start
    root.bind("<Return>", lambda event: submit())

    root.mainloop()

    return result["value"]


PUSHUP_LIMIT = get_pushup_target(DEFAULT_PUSHUP_LIMIT)
SELECTED_VIDEO_PATH, SELECTED_AUDIO_PATH = select_motivation_media(
    VIDEO_PATH, AUDIO_PATH
)

# -------------------------------
# Initialize components
# -------------------------------
cap = cv2.VideoCapture(0)

counter = PushUpCounter()
video = VideoOverlay(SELECTED_VIDEO_PATH)
audio = AudioPlayer(SELECTED_AUDIO_PATH)

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
