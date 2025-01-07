import pandas as pd
from flask import Flask, render_template, Response, request, jsonify
from ultralytics import YOLO
import cv2
import random
import time

app = Flask(__name__)

# Load Vocab.xlsx and prepare data
vocab_df = pd.read_excel('Vocab.xlsx')
vocab_dict = dict(zip(vocab_df['Arabic Letter'], vocab_df['Objects in English']))

# Load History.xlsx to track player progress
history_df = pd.read_excel('history.xlsx')

# Standardize column names for consistency
history_df.rename(
    columns={
        "Name": "name",
        "letters": "letter",
        "Detect": "detect",
        "Time": "time"
    },
    inplace=True,
)

# YOLO model
model = YOLO('yolov8n-oiv7.pt')

# Global variables for the game
selected_letter = None
target_classes = []
found = False
start_time = None
timer_duration = 60  # 60 seconds timer
camera = None  # Initialize as None


def initialize_resources():
    """Ensure resources like the camera are initialized."""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)


def select_random_letter():
    """Select a random letter and corresponding target classes."""
    global selected_letter, target_classes, found
    selected_letter = random.choice(list(vocab_dict.keys()))
    target_classes = [cls.strip().lower() for cls in vocab_dict[selected_letter].split(",")]
    found = False  # Reset the found state
    update_history_appearance(selected_letter)


def update_history_appearance(letter):
    """Update the appearance count for the selected letter."""
    global history_df
    # Check if the letter already exists in history
    if letter in history_df['letter'].values:
        history_df.loc[history_df['letter'] == letter, 'time'] += 1
    else:
        # Add a new row for the letter
        new_row = pd.DataFrame({
            'name': [''],  # User name will be added later
            'letter': [letter],
            'detect': ['FALSE'],
            'time': [1]
        })
        history_df = pd.concat([history_df, new_row], ignore_index=True)
    history_df.to_excel('history.xlsx', index=False)


def update_history_correct(letter):
    """Update the correct detection count for the letter."""
    global history_df
    if letter in history_df['letter'].values:
        history_df.loc[history_df['letter'] == letter, 'detect'] = 'TRUE'
    history_df.to_excel('history.xlsx', index=False)


def generate_frames():
    """Generate frames for video streaming and YOLO detection."""
    global found, start_time, timer_duration, camera
    initialize_resources()

    while True:
        success, frame = camera.read()
        if not success or found:
            break

        if start_time is None:
            start_time = time.time()

        results = model.predict(source=frame, verbose=False)
        annotated_frame = results[0].plot()

        # Check for target classes
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                class_name = result.names[class_id].lower()
                if class_name in target_classes:
                    found = True
                    update_history_correct(selected_letter)
                    break

        if found:
            cv2.putText(annotated_frame, "Correct!!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if start_time:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, timer_duration - int(elapsed_time))
            cv2.putText(annotated_frame, f"Time Left: {remaining_time}s", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if remaining_time == 0:
            if not found:
                cv2.putText(annotated_frame, "Time's Up!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            break

        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()


@app.route('/')
def index():
    """Render the index page."""
    return render_template('Index.html')


@app.route('/Game')
def game():
    """Render the game page."""
    global start_time
    select_random_letter()
    start_time = None  # Reset the timer
    return render_template('Game.html', letter=selected_letter, timer=timer_duration)


@app.route('/video_feed')
def video_feed():
    """Stream video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/update_timer')
def update_timer():
    """Update the game timer."""
    global start_time, timer_duration
    if start_time is None:
        return jsonify({"remaining_time": timer_duration})

    elapsed_time = time.time() - start_time
    remaining_time = max(0, timer_duration - int(elapsed_time))
    return jsonify({"remaining_time": remaining_time})


@app.route('/results')
def results():
    """Render the results page."""
    user_name = request.args.get('name', 'Unknown')
    filtered_df = history_df[history_df['name'] == user_name]

    if filtered_df.empty:
        return render_template('Results.html', user_name=user_name, results=[], error="لا توجد بيانات لهذا المستخدم.")

    letter_counts = filtered_df['letter'].value_counts().to_dict()
    correct_count = filtered_df[filtered_df['detect'].str.lower() == 'true'].shape[0]

    results = [(letter, count, correct_count) for letter, count in letter_counts.items()]
    return render_template('Results.html', user_name=user_name, results=results)


if __name__ == '__main__':
    app.run(debug=True)
