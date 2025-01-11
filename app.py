import pandas as pd
from flask import Flask, render_template, Response, request, jsonify
from ultralytics import YOLO
import cv2
import random
import time

app = Flask(__name__)

vocab_df = pd.read_excel('data/objects.xlsx')
vocab_dict = dict(zip(vocab_df['Arabic Letter'], vocab_df['Objects in English']))
weights={'ا': 3.626800535671137, 'س': 2.561040452199646, 'ش': 1.1115987744649718, 'ح': 1.4955451544254066,
          'م': 4.387991868972226, 'ج': 0.6451356060606059, 'ه': 0.6451356060606059, 'ت': 1.6401356060606058, 
          'ك': 2.4483051849028694, 'ل': 1.2412106522609043, 'ق': 0, 'ص': 0.8406952688172042, 
          'ب': 0, 'ن': 2.6880236307608127, 'ع': 1.360584329403095, 'ف': 3.1039120937662927, 
          'د': 1.3219472469036115, 'و': 0.5254632653061224, 'ز': 0.7644755825242718, 'ط': 0.23334381408065616}


got_name = False
model = YOLO('model/Model.pt')

selected_letter = None
target_classes = []
found = False
start_time = None
timer_duration = 30
player_name = "Unknown"

def initialize_resources():
    global camera
    camera = cv2.VideoCapture(0)

def select_random_letter():
    global selected_letter, target_classes, found
    total_weight = sum(weights.values())
    probabilities = {k: v / total_weight for k, v in weights.items()}
    
    selected_letter = random.choices(list(probabilities.keys()), weights=probabilities.values(), k=1)[0]
    target_classes = [cls.strip().lower() for cls in vocab_dict[selected_letter].split(",")]
    found = False


def update_history(player_name, letter, time_taken):
    try:
        history_df = pd.read_excel('data/history.xlsx')
    except FileNotFoundError:
        history_df = pd.DataFrame(columns=['Name', 'Letter', 'Time', 'Detect'])
    
    new_entry = {'Name': player_name, 'Letter': letter, 'Time': time_taken, 'Detect': found}
    history_df = pd.concat([history_df, pd.DataFrame([new_entry])], ignore_index=True)

    history_df.to_excel('data/history.xlsx', index=False)

def analyze_player(player_name):
    try:
        df = pd.read_excel('data/history.xlsx')
    except FileNotFoundError:
        return []

    player_df = df[df['Name'] == player_name]

    analysis_df = player_df.groupby('Letter').agg(
        total_games=('Detect', 'count'),
        detect_false=('Detect', lambda x: (x == False).sum()),
        detect_true=('Detect', lambda x: (x == True).sum())
    ).reset_index()

    filtered_letters = analysis_df[
        (analysis_df['total_games'] > 5) & (analysis_df['detect_false'] > analysis_df['detect_true'])
    ]['Letter'].tolist()

    return filtered_letters

def generate_frames():
    global found, start_time, camera, timer_duration
    if not camera.isOpened():
        initialize_resources()

    while True:
        success, frame = camera.read()
        if not success or found:
            break

        if start_time is None:
            start_time = time.time()

        elapsed_time = time.time() - start_time if start_time is not None else 0
        remaining_time = max(0, timer_duration - int(elapsed_time))

        results = model.predict(source=frame, verbose=False)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)

                class_id = int(box.cls)
                class_name = result.names[class_id].lower()
                if class_name in target_classes:
                    found = True
                    update_history(player_name, selected_letter, (timer_duration - round(elapsed_time, 2)))
                    break

            if found:
                break

        if found:
            cv2.putText(frame, "Correct!!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.putText(frame, f"Time Left: {remaining_time}s", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        if remaining_time == 0:
            if not found:
                update_history(player_name, selected_letter, 0)
                cv2.putText(frame, "Fail!!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()

def get_player_name():
    global player_name, got_name
    if not got_name:
        player_name = request.args.get('name', 'Player')
        got_name = True


@app.route('/')
def index():
    global got_name
    got_name = False
    return render_template('Index.html')


@app.route('/Game')
def game():
    global start_time, player_name
    select_random_letter()
    start_time = None
    get_player_name()
    return render_template('Game.html', letter=selected_letter, timer=timer_duration, player_name=player_name)

@app.route('/video_feed')
def video_feed():
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

@app.route('/results')
def results():
    global player_name
    history_df = pd.read_excel('data/history.xlsx')
    filtered_df = history_df[history_df['Name'] == player_name]
    
    if filtered_df.empty:
        return render_template('Results.html', user_name=player_name, results=[], error="لا توجد بيانات لهذا المستخدم.")
    
    letter_counts = filtered_df['Letter'].value_counts().to_dict()
    correct_counts = filtered_df[filtered_df['Detect'] == True].groupby('Letter').size().to_dict()

    results = []
    for letter, count in letter_counts.items():
        correct_count = correct_counts.get(letter, 0)
        results.append((letter, count, correct_count))
    
    player_mistakes = analyze_player(player_name)
    
    return render_template('Results.html', user_name=player_name, results=results, player_mistakes=player_mistakes)


@app.route('/leaderboard')
def leaderboard():
    history_df = pd.read_excel('data/history.xlsx')

    history_df.rename(
        columns={
            "Name": "name",
            "letters": "letters",
            "Detect": "detect",
            "Time": "time"
        },
        inplace=True,
    )

    leaderboard_data = (
        history_df.groupby('name')['time']
        .mean()
        .reset_index()
        .sort_values(by='time', ascending=True)
    )

    leaderboard_data = leaderboard_data[leaderboard_data['time'] > 0.0]
    leaderboard_data['time'] = leaderboard_data['time'].round(2)  
    leaderboard_data = leaderboard_data.head(5)
    leaderboard = list(leaderboard_data.itertuples(index=False, name=None))

    return render_template('leaderboard.html', leaderboard=leaderboard)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=502, debug=True)
