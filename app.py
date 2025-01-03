from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Index.html')  # أو أي اسم للصفحة الأولى

@app.route('/Game')
def game():
    return render_template('Game.html')   # الصفحة الثانية

if __name__ == '__main__':
    app.run(debug=True)
