import pandas as pd
from flask import Flask, render_template, Response
from ultralytics import YOLO
import cv2
import random

app = Flask(__name__)

# Load Vocab.xlsx and prepare data
vocab_df = pd.read_excel('Vocab.xlsx')
vocab_dict = dict(zip(vocab_df['Arabic Letter'], vocab_df['Objects in English']))

# YOLO model
model = YOLO('yolov8n-oiv7.pt')

# Web Camera
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise RuntimeError('Error: Unable to access the camera.')

# Global variables for the game
selected_letter = None
target_classes = []
found = False

def select_random_letter():
    global selected_letter, target_classes
    selected_letter = random.choice(list(vocab_dict.keys()))
    target_classes = vocab_dict[selected_letter].split(",")  # Assuming objects are comma-separated

def generate_frames():
    global found
    while True:
        success, frame = camera.read()
        if not success or found:
            break
        
        # YOLO Detection
        results = model.predict(source=frame, verbose=False)
        annotated_frame = results[0].plot()
        
        # Check for target classes
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                class_name = result.names[class_id]
                if class_name in target_classes:
                    found = True
                    break
            if found:
                break
        
        # Show "Correct!!" if found
        if found:
            cv2.putText(annotated_frame, "Correct!!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode frame
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/Game')
def game():
    select_random_letter()  # Pick a new letter and targets
    return render_template('Game.html', letter=selected_letter)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
