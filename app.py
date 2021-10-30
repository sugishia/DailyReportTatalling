from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_manager, login_user, login_required, logout_user
#import flask_bootstrap

app = Flask(__name__)
#db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/display', methods=['GET', 'POST'])
def display():
    if request.method == 'GET':
        return render_template('display.html')

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        return redirect(url_for('display'))
    return render_template('report.html')