from flask import request, redirect, render_template, url_for
from app import app

from datetime import datetime
import calendar

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('display'))
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/display', methods=['GET', 'POST'])
def display():
    if request.method == 'GET':
        return render_template('display.html')

@app.route('/report', methods=['GET', 'POST'])
def report():
    today = datetime.now()
    if request.method == 'POST':
        month = request.form['month']
        day = request.form['day']
        print(month, day)
        return redirect(url_for('display'))
    return render_template('report.html', today={'month':today.month, 'day':today.day}, days=calendar.monthrange(today.year, today.month)[1] + 1)


if __name__ == '__main__':
    app.run(debug=True)