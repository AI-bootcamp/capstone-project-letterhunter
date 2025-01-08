# 🏹 Letter Hunter: Arabic Learning Game

## 🛠️ Project Overview

**Letter Hunter** is an educational game designed to make learning Arabic letters and words engaging for children. Players enter their names and receive a random Arabic letter, after which they must quickly identify an object that starts with the letter's Arabic translation. The game tracks player performance across multiple rounds and ranks players based on their history compared to others. The rankings are determined by the average time taken to identify objects and the accuracy of their answers.

---

## 📂 Directory Structure

```plaintext
.
├── static
│   ├── css
│   │   └── styles.css          # Styling for the game interface
│   ├── images                  # Game-related images
│   └── js
│       └── script.js           # JavaScript for game logic and animations
├── templates
│   └── index.html              # HTML for the game interface
├── app.py                      # Flask application file
├── model
│   └── yolov8n.pt              # YOLOv8n model for object detection
├── data
│   ├── annotated_data.csv      # Annotated data used for training
│   ├── raw_images              # Collected dataset of images
│   └── roboflow_annotations    # Roboflow annotations and augmentation
├── README.md                   # Project documentation (this file)
├── requirements.txt            # List of dependencies for the project
└── utils
    ├── performance_analysis.py # Functions for player performance tracking
    └── object_translation.py   # Functions to get Arabic translations for objects
```

---

## ✨ Key Features

- **Personalized Gameplay**: Players enter their names and receive a unique experience.
- **Random Letter Selection**: A new random Arabic letter is provided in each round.
- **Object Recognition with YOLOv8n**: Players must find an object that starts with the given letter, detected using a YOLOv8n computer vision model.
- **Performance Tracking**: Tracks the player's accuracy and response time.
- **Player Ranking**: Ranks players based on average response time and accuracy compared to other players.
- **Child-Friendly UI**: The interface is designed to be engaging and easy to use for children.

---

## 🎯 Objectives

1. Make Arabic learning fun and interactive for children.
2. Build a robust computer vision model for accurate object detection.
3. Provide performance insights and encourage friendly competition among players.
4. Foster language recognition and object association through play.

---

## 🚀 Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone [https://github.com/your-repository/letter-hunter.git](https://github.com/AI-bootcamp/capstone-project-letterhunter.git)
   cd letter-hunter
   ```

2. **Set Up the Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**

   Launch the Flask app:

   ```bash
   python app.py
   ```

5. **Access the Game**

   Open your browser and visit:

   ```plaintext
   http://127.0.0.1:5000
   ```

---

## ⚙️ How It Works

1. **Data Collection and Annotation**:
   - We collected images of common objects and annotated them using **Roboflow**.

2. **Model Training**:
   - The YOLOv8n-oiv7 model was trained on the annotated dataset to detect objects.

3. **Gameplay Flow**:
   - A player enters their name and clicks "Start Game".
   - A random Arabic letter is displayed.
   - The player must identify an object that starts with the letter.
   - The object is verified using the computer vision model.
   - The player's performance is analyzed based on:
     - **Time taken** to correctly identify the object.
     - **Accuracy** of object-letter matches.

4. **Performance Analysis**:
   - The system tracks the player’s performance history and compares it to other players.
   - Ranks are updated based on:
     - Average time taken to identify objects.
     - Percentage of correct answers.

---

## 📸 Screenshots

![image](https://github.com/user-attachments/assets/d5dc6a79-78ae-4353-bdb4-478868e931a2)


---

## 🔮 Future Enhancements

- **Additional Language Support**: Add translations for more languages, more levels.
- **Expanded Dataset**: Collect more annotated data for improved model performance, finetuning the model.
- **Two-Player Mode**: Add real-time challenges where two players compete to identify objects matching their Arabic letters.
- **Mobile App**: Create a mobile-friendly version for easier access.

---

## 👥 Team

This project was developed by a dedicated team of AI and software enthusiasts:

1. **Shaden**: Data collection and Software engineering and Ideation and Model training.
2. **Salwa**: Data collection and Data proccesing and Analysis and UI/UX design.
3. **Mohammed**: Frontend design and software engineering and Structure and Analysis.
4. **Abdulkarim**: Frontend design and software engineering and Logic Design, Problem Solving.

---

## 📜 Credits

This project was inspired by educational initiatives promoting fun language learning. Special thanks to **Roboflow** for providing an intuitive annotation platform and the open-source **YOLOv8** model for object detection.
