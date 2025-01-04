from flask import Flask, render_template, Response
from ultralytics import YOLO
import cv2

app = Flask(__name__)

# تحميل نموذج YOLO
model = YOLO('yolov8n-oiv7.pt')

# تهيئة كاميرا الويب
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError('خطأ: لا يمكن الوصول إلى الكاميرا.')

def generate_frames():
    frame_skip = 3
    frame_count = 0
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame_count += 1
            if frame_count % frame_skip == 0:
                # إجراء الكشف باستخدام YOLO
                results = model.predict(source=frame, verbose=False)
                annotated_frame = results[0].plot()

                # ترميز الإطار بتنسيق JPEG
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame = buffer.tobytes()

                # بث الإطار
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                continue

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/Game')
def game():
    return render_template('Game.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
