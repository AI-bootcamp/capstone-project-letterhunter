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
weights={'ا': 2.737287179487179, 'س': 2.4398833333333334, 'ش': 1.4268947368421052, 'ح': 1.5263110000000002, 
         'م': 5.07463440860215, 'ج': 0.9453642857142857, 
         'ه': 0.9453642857142857, 'ت': 1.8910181318681318, 'ك': 2.3700067073170734, 'ل': 1.4527200909090912,
         'ق': 1.2338766214773247, 'ص': 0.8955, 'ب': 0.5306666666666666, 'ن': 2.898649377604724,
         'ع': 1.2680267585571052, 'ف': 3.227333333333333, 'د': 1.4978676190476188, 'و': 0.6626666666666665, 
         'ز': 0.7314222535211268, 'ط': 0.0}
got_name = False
# YOLO model
model = YOLO('best_1.pt')

# Initialize global variables
selected_letter = None
target_classes = []
found = False
start_time = None
timer_duration = 10  # 10 seconds timer
player_name = "Unknown"  # Default player name

def initialize_resources():
    global camera
    camera = cv2.VideoCapture(0)

def select_random_letter():
    global selected_letter, target_classes, found
    
    # Normalize the weights to sum to 1 (calculate probabilities)
    total_weight = sum(weights.values())
    probabilities = {k: v / total_weight for k, v in weights.items()}
    
    # Select a letter based on the weighted probabilities
    selected_letter = random.choices(list(probabilities.keys()), weights=probabilities.values(), k=1)[0]
    target_classes = [cls.strip().lower() for cls in vocab_dict[selected_letter].split(",")]  # Clean class names and convert to lowercase
    found = False  # Reset the found state


def update_history(player_name, letter, time_taken):
    # Load history
    try:
        history_df = pd.read_excel('history.xlsx')
    except FileNotFoundError:
        history_df = pd.DataFrame(columns=['Name', 'Letter', 'Time', 'Detect'])
    
    # Add the new entry
    new_entry = {'Name': player_name, 'Letter': letter, 'Time': time_taken, 'Detect': found}
    history_df = pd.concat([history_df, pd.DataFrame([new_entry])], ignore_index=True)

    # Save the updated history
    history_df.to_excel('history.xlsx', index=False)

def analyze_player(player_name):
    try:
        df = pd.read_excel('history.xlsx')
    except FileNotFoundError:
        return []

    # Filter rows for the given player
    player_df = df[df['Name'] == player_name]

    # Group by letters played
    analysis_df = player_df.groupby('Letter').agg(
        total_games=('Detect', 'count'),
        detect_false=('Detect', lambda x: (x == False).sum()),
        detect_true=('Detect', lambda x: (x == True).sum())
    ).reset_index()

    # Filter letters with more than 5 games and Detect=False > Detect=True
    filtered_letters = analysis_df[
        (analysis_df['total_games'] > 5) & (analysis_df['detect_false'] > analysis_df['detect_true'])
    ]['Letter'].tolist()

    return filtered_letters

def generate_dashboard_data():
    try:
        # Load the game history
        df = pd.read_excel('game_history.xlsx')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Name', 'Time'])  # Return empty DataFrame if file not found

    # Filter where 'Detect' is True
    filtered_df = df[df['Detect'] == True]

    # Calculate the average time for each player
    average_time_df = filtered_df.groupby('Name', as_index=False)['Time'].mean()

    # Sort by average time
    sorted_df = average_time_df.sort_values(by='Time', ascending=True)

    # Return the top 5 players
    return sorted_df.head(5)

def generate_frames():
    global found, start_time, camera, timer_duration
    if not camera.isOpened():
        initialize_resources()

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

        # Timer countdown
        elapsed_time = time.time() - start_time if start_time is not None else 0
        remaining_time = max(0, timer_duration - int(elapsed_time))

        # Check for target classes
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                class_name = result.names[class_id].lower()
                if class_name in target_classes:
                    found = True
                    elapsed_time = round(time.time() - start_time, 2)
                    update_history(player_name, selected_letter, elapsed_time)
                    break

        # Show "Correct!!" if target is found
        if found:
            cv2.putText(annotated_frame, "Correct!!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display remaining time
        cv2.putText(annotated_frame, f"Time Left: {remaining_time}s", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # If time is up and target not found, display "Time's Up" and stop the camera
        if remaining_time == 0:
            if not found:
                update_history(player_name, selected_letter, 0)
                cv2.putText(annotated_frame, "Fail!!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            break
        

        # Encode frame for streaming
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()

def get_player_name():
    global player_name, got_name
    if not got_name:
        player_name = request.args.get('name', 'Player')  # Retrieve player's name
        got_name = True


@app.route('/')
def index():
    global got_name
    got_name = False
    return render_template('Index.html')


@app.route('/Game')
def game():
    global start_time, player_name
    select_random_letter()  # Pick a new letter and targets
    start_time = None  # Reset the timer
    get_player_name()
    return render_template('Game.html', letter=selected_letter, timer=timer_duration, player_name=player_name)

@app.route('/Dashboard')
def dashboard():
    # Generate the dashboard data
    top_players_df = generate_dashboard_data()
    return render_template('Dashboard.html', top_players=top_players_df.to_dict(orient='records'))

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

@app.route('/Results')
def results():
    """Render the results page."""
    global player_name
    user_name = player_name
    history_df = pd.read_excel('history.xlsx')
    filtered_df = history_df[history_df['Name'] == user_name]
    if filtered_df.empty:
        return render_template('Results.html', user_name=user_name, results=[], error="لا توجد بيانات لهذا المستخدم.")
    letter_counts = filtered_df['Letter'].value_counts().to_dict()
    correct_count = filtered_df['Detect'].sum()
    results = [(letter, count, correct_count) for letter, count in letter_counts.items()]
    return render_template('Results.html', user_name=user_name, results=results)


@app.route('/leaderboard')
def leaderboard():
    # Load the Excel file
    history_df = pd.read_excel('history.xlsx')

    # Rename columns to standard format
    history_df.rename(
        columns={
            "Name": "name",
            "letters": "letters",
            "Detect": "detect",
            "Time": "time"
        },
        inplace=True,
    )

    # Calculate the average time for each name, excluding averages of 0.0
    leaderboard_data = (
        history_df.groupby('name')['time']
        .mean()
        .reset_index()
        .sort_values(by='time', ascending=True)
    )

    # Exclude names with an average time of 0.0
    leaderboard_data = leaderboard_data[leaderboard_data['time'] > 0.0]

    # Convert the result to a list of tuples for rendering
    leaderboard = list(leaderboard_data.itertuples(index=False, name=None))

    return render_template('leaderboard.html', leaderboard=leaderboard)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=502, debug=True)
