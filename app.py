from flask import Flask, render_template, request, Response
import sqlite3
import csv

app = Flask(__name__)

questions = [
    
    {
        "id": 1,
        'question': 'What is the capital of France?',
        'options': ['A. Berlin', 'B. Madrid', 'C. Paris', 'D. Rome'],
        'answer': 'C. Paris'
    },
    {
        "id": 2,
        'question': 'Which planet is known as the Red Planet?',
        'options': ['A. Earth', 'B. Mars', 'C. Jupiter', 'D. Saturn'],
        'answer': 'B. Mars'
    },
    {
        "id": 3,
        'question': 'What is the largest ocean on Earth?',
        'options': ['A. Atlantic Ocean', 'B. Indian Ocean', 'C. Arctic Ocean', 'D. Pacific Ocean'],
        'answer': 'D. Pacific Ocean'
    },
    {    "id": 4,
        'question': 'Who wrote "To Kill a Mockingbird"?',
        'options': ['A. Harper Lee', 'B. Mark Twain', 'C. Ernest Hemingway', 'D. F. Scott Fitzgerald'],
        'answer': 'A. Harper Lee'
    },
    {    "id": 5,
        'question': 'What is the chemical symbol for gold?',
        'options': ['A. Au', 'B. Ag', 'C. Fe', 'D. Cu'],
        'answer': 'A. Au'
    }
]

def create_db():
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS results (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     student_name TEXT,
                     student_id INTEGER unique,
                     department TEXT,
                     score INTEGER
                   )
                    ''')

    conn.commit()
    conn.close()

create_db()    

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/quiz', methods=['POST'])
def quiz():

    student_name = request.form.get('name')
    student_id = request.form.get('student_id')
    department = request.form.get('department')

    return render_template('quiz.html', questions=questions,
                           student_name=student_name, student_id=student_id, department=department)

@app.route('/submit', methods=['POST'])
def submit():

    student_name = request.form.get('student_name')
    student_id = request.form.get('student_id')
    department = request.form.get('department')

    print(f"Student Name: {student_name}, Student ID: {student_id}, Department: {department}")

    score = 0

    for question in questions:
        user_answer = request.form.get(f'question_{question["id"]}')

        if user_answer == question['answer']:
            score += 1

    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO results (student_name, student_id, department, score) VALUES (?, ?, ?, ?)
        """,
        (student_name, student_id, department, score)
    )
    conn.commit()
    conn.close()

    return "Submitted"
    

    # Process the submitted quiz answers
@app.route('/results')
def results():

    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()

    # cursor.execute("Delete From results")
    # cursor.execute("Delete From sqlite_sequence WHERE name='results'")

    conn.commit()

    cursor.execute("SELECT * FROM results")
    print("Inserting data into the database...")
    data = cursor.fetchall()

    conn.close()
    
    
    return render_template('results.html', data=data)

@app.route("/download")
def download():
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM results")
    data = cursor.fetchall()

    conn.close()

    output = []
    output.append(['ID', 'Student Name', 'Student ID', 'Department', 'Score'])
    output.extend(data)

    # Create a CSV response
    def generate():
        yield ','.join(['ID', 'Student Name', 'Student ID', 'Department', 'Score']) + '\n'
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=results.csv'})



if __name__ == '__main__':
    app.run(debug=True)