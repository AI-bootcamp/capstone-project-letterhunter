import pandas as pd
from flask import Flask, render_template, Response, request, jsonify
from ultralytics import YOLO
import cv2
import random
import time

app = Flask(__name__)

vocab_df = pd.read_excel('data/objects.xlsx')
vocab_dict = dict(zip(vocab_df['Arabic Letter'], vocab_df['Objects in English']))
weights={'ا': 3.308243902439024,
 'س': 5.1516485199004975,
 'ش': 1.6554883442737016,
 'ح': 2.0530558754413644,
 'م': 6.888193361089029,
 'ج': 0.922940709068709,
 'ه': 0.6498292743922743,
 'ت': 0.6498292743922743,
 'ك': 2.839570996582834,
 'ل': 1.1874371052631578,
 'ق': 1.3290345007345672,
 'ص': 2.661763281705795,
 'ب': 1.3801684701373518,
 'ن': 3.443340762186038,
 'ع': 1.3106106739926742,
 'ف': 3.857348473945362,
 'د': 1.1809699212314098,
 'و': 0.9974996424733138,
 'ز': 1.061254237711409,
 'ط': 1.7735151014354575}


got_name = False
model = YOLO('model/Model_Final.pt')

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
