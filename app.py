from flask import Flask, render_template, request, Response, session
import os
import time
import psycopg
import csv

ADMIN_PASSWORD = "stats@2026"

app = Flask(__name__)
app.secret_key = "quiz-secret-key-2026"

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg.connect(DATABASE_URL)

def create_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            student_name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            department TEXT,
            score INTEGER NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

questions = [
    
    {
        "id": 1,
        'question': 'Which measure is most affected by extreme values?',
        'options': ['A. Median', 'B. Mode', 'C. Quartile', 'D. Mean'],
        'answer': 'C. Median'
    },
    {
        "id": 2,
        'question': 'The mean of the observations 4,8,10,12,16 is?',
        'options': ['A. 10', 'B. 12', 'C. 14', 'D. 16'],
        'answer': 'B. 12'
    },
    {
        "id": 3,
        'question': 'If X = 2,4,6,8,10, what is the median?',
        'options': ['A. 6', 'B. 7', 'C. 8', 'D. 9'],
        'answer': 'A. 6'
    },
    {   
         "id": 4,
        'question': 'If P(A) = 0.5 and P(B) = 0.3, what is P(A ∩ B) if A and B are independent?',
        'options': ['A. 0.15', 'B. 0.2', 'C. 0.3', 'D. 0.5'],
        'answer': 'A. 0.15'
    },
    {   
         "id": 5,
        'question': 'A random variable follows Binomial distribution with parameters n and p. What is the mean of this distribution?',
        'options': ['A. np', 'B. n(1-p)', 'C. p(1-p)', 'D. n²p'],
        'answer': 'A. np'
    },
    {
        "id": 6,
        'question': 'What is the probability of getting exactly 3 heads in 5 tosses of a fair coin?',
        'options': ['A. 0.3125', 'B. 0.5', 'C. 0.25', 'D. 0.375'],
        'answer': 'A. 0.3125'   
    },
    {
        "id": 7,
        'question': 'What is the standard deviation of a standard normal distribution?',
        'options': ['A. 0', 'B. 1', 'C. 2', 'D. 3'],
        'answer': 'B. 1'
    },
    {
        "id": 8,
        'question': 'If the correlation coefficient between two variables is -0.8, what does it indicate about the relationship between the variables?',
        'options': ['A. Strong positive relationship', 'B. Weak positive relationship', 'C. Strong negative relationship', 'D. Weak negative relationship'],
        'answer': 'C. Strong negative relationship' 
    },
    {
        "id": 9,
        'question': 'What is the probability of getting at least one 6 in four rolls of a fair die?',
        'options': ['A. 0.5177', 'B. 0.5', 'C. 0.25', 'D. 0.75'],
        'answer': 'A. 0.5177'           
    },
    {
        "id": 10,
        'question': 'If the mean of a dataset is 50 and the standard deviation is 5, what is the z-score of a value of 60?',
        'options': ['A. 1', 'B. 2', 'C. 3', 'D. 4'],
        'answer': 'B. 2'    
    }
]



create_db()    

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/quiz', methods=['POST'])
def quiz():

    if request.method == 'POST':

        # If quiz is already active, do not restart the timer
        if 'quiz_start_time' not in session:

            session['student_name'] = request.form.get('name')
            session['student_id'] = request.form.get('student_id')
            session['department'] = request.form.get('department')

            session['quiz_start_time'] = time.time()

    # Get student information from session
    student_name = session.get('student_name')
    student_id = session.get('student_id')
    department = session.get('department')

    # If there is no active quiz, go to login
    if not student_name or not student_id or not department:
        return render_template('login.html')

    # Calculate remaining time
    elapsed = time.time() - session['quiz_start_time']
    remaining_time = max(0, int(30 * 60 - elapsed))

    return render_template(
        'quiz.html',
        questions=questions,
        student_name=student_name,
        student_id=student_id,
        department=department,
        remaining_time=remaining_time
    )




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

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO results
            (student_name, student_id, department, score)
            VALUES (%s, %s, %s, %s)
            """,
            (student_name, student_id, department, score)
        )
        conn.commit()

    except psycopg.errors.UniqueViolation:
        conn.rollback()
        cursor.close()
        conn.close()
        return "This Student ID has already submitted the quiz. You cannot submit again."

    cursor.close()
    conn.close()

    session.clear()

    return "Submitted"

    

    # Process the submitted quiz answers
@app.route('/results')
def results():

    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Unauthorized access. Please provide the correct password."

    conn = get_db()
    cursor = conn.cursor()


    conn.commit()

    cursor.execute("SELECT * FROM results ORDER BY ID")
    print("Inserting data into the database...")
    data = cursor.fetchall()

    conn.close()
    
    
    return render_template('results.html', data=data)

@app.route("/download")
def download():

    conn = get_db()
    cursor = conn.cursor()


    cursor.execute("SELECT * FROM results ORDER BY ID")
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

create_db()

if __name__ == '__main__':
    app.run(debug=True)