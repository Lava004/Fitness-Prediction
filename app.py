from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

EXCEL_FILE_PATH = 'D:\Fitness Prediction\Shawn Bieber medical dataset.xlsx'

USERS = {
    'patient': {'username': 'patient', 'password': 'patient123', 'role': 'Patient'},
    'doctor': {'username': 'doctor', 'password': 'doctor123', 'role': 'Doctor'}
}

def calculate_fitness_score():
    xls = pd.ExcelFile(EXCEL_FILE_PATH)
    appointment_data = xls.parse('Appointment Table')
    fitness_score = appointment_data['Health Score'].mean()

    fitness_data = xls.parse('Fitness Data')
    dates = pd.to_datetime(fitness_data['Date'])
    bmi_values = fitness_data['BMI']

    plt.figure(figsize=(10, 6))
    plt.plot(dates, bmi_values, marker='o', color='b', label="BMI over time")
    plt.title("Patient's BMI Trend Over Time")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.legend()
    plt.grid()

    graph_path = 'static/bmi_trend_graph.png'
    plt.savefig(graph_path)
    plt.close()

    return fitness_score

@app.route('/')
def home():
    if 'username' in session:
        sheets = pd.ExcelFile(EXCEL_FILE_PATH).sheet_names
        if session.get('role') == 'Patient':
            fitness_score = calculate_fitness_score()
            return render_template('index.html', sheet_names=sheets, role='Patient', fitness_score=round(fitness_score, 2))
        return render_template('index.html', sheet_names=sheets, role='Doctor')
    else:
        return redirect(url_for('login'))

@app.route('/view_sheet/<sheet_name>', methods=['GET', 'POST'])
def view_sheet(sheet_name):
    if 'username' in session:
        role = session.get('role')
        sheets = pd.ExcelFile(EXCEL_FILE_PATH)
        sheet_data = sheets.parse(sheet_name)

        if sheet_data is not None:
            if request.method == 'POST' and role == 'Doctor':
                new_row = {col: request.form.get(col, "") for col in sheet_data.columns}
                sheet_data = pd.concat([sheet_data, pd.DataFrame([new_row])], ignore_index=True)

                with pd.ExcelWriter(EXCEL_FILE_PATH) as writer:
                    for name in sheets.sheet_names:
                        data = sheet_data if name == sheet_name else sheets.parse(name)
                        data.to_excel(writer, sheet_name=name, index=False)

                return redirect(url_for('view_sheet', sheet_name=sheet_name))

            table_html = sheet_data.to_html()
            return render_template('view_sheet.html', sheet_name=sheet_name, table_html=table_html, role=role)
        else:
            return f"<h3>Sheet '{sheet_name}' not found!</h3>"
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('home'))
        else:
            return "<h3>Invalid credentials</h3>"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)











