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

# YOLO model
model = YOLO('yolov8n-oiv7.pt')

def initialize_resources():
    global camera, model
    camera = cv2.VideoCapture(0)

# Global variables for the game
selected_letter = None
target_classes = []
found = False
start_time = None
timer_duration = 60#60 seconds timer

def select_random_letter():
    global selected_letter, target_classes, found
    selected_letter = random.choice(list(vocab_dict.keys()))
    target_classes = [cls.strip().lower() for cls in vocab_dict[selected_letter].split(",")]  # Clean class names and convert to lowercase
    found = False  # Reset the found state
    update_history_appearance(selected_letter)

def update_history_appearance(letter):
    global history_df
    # Increment the "how many time appear" counter for the selected letter
    if letter in history_df['Letter'].values:
        history_df.loc[history_df['Letter'] == letter, 'how many time appear'] += 1
    else:
        # Create a new row as a DataFrame
        new_row = pd.DataFrame({
            'ID': [''],  # We will update the ID after the player is identified
            'Letter': [letter],
            'how many time appear': [1],
            'how much correct': [0]
        })
        # Use pd.concat to add the new row
        history_df = pd.concat([history_df, new_row], ignore_index=True)
    
    # Save the updated history back to Excel
    history_df.to_excel('history.xlsx', index=False)


def update_history_correct(letter):
    global history_df
    # Increment the "how much correct" counter if the letter is detected
    if letter in history_df['Letter'].values:
        history_df.loc[history_df['Letter'] == letter, 'how much correct'] += 1
    # Save the updated history back to Excel
    history_df.to_excel('history.xlsx', index=False)

def generate_frames():
    global found, start_time, timer_duration, camera
    if not camera.isOpened():
        initialize_resources()  # Ensure the camera is initialized

    while True:
        success, frame = camera.read()
        if not success or found:
            break

        # Start timer when the game starts
        if start_time is None:
            start_time = time.time()

        # YOLO Detection
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

        # Show "Correct!!" if found
        if found:
            cv2.putText(annotated_frame, "Correct!!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Timer countdown
        if start_time is not None:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, timer_duration - int(elapsed_time))
            cv2.putText(annotated_frame, f"Time Left: {remaining_time}s", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # If time is up and not found, display "Time's Up" and stop the camera
        if remaining_time == 0:
            if not found:
                cv2.putText(annotated_frame, "Time's Up!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            break

        # Encode frame
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Optionally release the camera here if needed
    camera.release()

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/Game')
def game():
    global start_time
    select_random_letter()  # Pick a new letter and targets
    start_time = None  # Reset the timer
    return render_template('Game.html', letter=selected_letter, timer=timer_duration)

@app.route('/video_feed')
def video_feed():
    # Ensure resources are initialized before streaming
    initialize_resources()
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/update_timer')
def update_timer():
    global start_time, timer_duration
    if start_time is None:
        return jsonify({"remaining_time": timer_duration})
    
    elapsed_time = time.time() - start_time
    remaining_time = max(0, timer_duration - int(elapsed_time))
    return jsonify({"remaining_time": remaining_time})


if __name__ == '__main__':
    app.run(debug=True)
