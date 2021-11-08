from flask import request, redirect, render_template, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user
from flask_login.utils import confirm_login
from models import db, DailyReport, Branch
from app import app, login_manager

from datetime import datetime
import calendar

@login_manager.user_loader
def load_user(branch_id):
    return Branch.query.get(int(branch_id))

#@app.errorhandler(401)
#def 

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_name = request.form.get('login_name')
        password = request.form.get('password')

        branch = Branch.query.filter_by(login_name=login_name).first()
        print(branch.branch_name)
        if branch and check_password_hash(branch.password, password):
            login_user(branch)
            return redirect(url_for('display'))
        else:
            return render_template('login.html', error='ユーザー名かパスワードが間違っています')

    return render_template('login.html')

@app.route('/create_branch', methods=['GET','POST'])
#@login_required
def create_branch():
    if request.method == 'POST':
        branch_name = request.form.get('branch_name')
        login_name = request.form.get('login_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_commissioner = request.form.get('is_commissioner')
        print(request.form.get('is_commissioner'))
        if password != confirm_password:
            return render_template('create_branch.html', branch_name=branch_name, login_name=login_name, password=password, confirm_password=confirm_password, is_commissioner=is_commissioner, error='【要確認】パスワードと確認用パスワードが異なります')
        
        with db.session.begin(subtransactions=True):
            new_branch = Branch(branch_name=branch_name, login_name=login_name, password=generate_password_hash(password, method='sha256'), is_commissioner=judge_commissioner(is_commissioner))
            print(new_branch, branch_name, login_name, password, is_commissioner)
            db.session.add(new_branch)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('create_branch.html')



@app.route('/display', methods=['GET', 'POST'])
@login_required
def display():
    if request.method == 'GET':
        return render_template('display.html')

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    today = datetime.now()
    if request.method == 'POST':

        month = request.form['month']
        day = request.form['day']
        date = datetime.strptime(f'{datetime.now().year}/{month}/{day}', '%Y/%m/%d')

        in_party = request.form['in_party']
        out_party = request.form['out_party']

        readed = request.form['readed']

        discuss = False
        if request.form['discuss'] == 'True':
            discuss = True

        print(f'date:{date}, in_party:{in_party}, out_party:{out_party}, readed:{readed}, discuss:{discuss}')
        with db.session.begin(subtransactions=True):
            new_report = DailyReport(date, in_party, out_party, readed, discuss=False)
            db.session.add(new_report)
        db.session.commit()

        return redirect(url_for('display'))
    return render_template('report.html', today={'month':today.month, 'day':today.day}, days=calendar.monthrange(today.year, today.month)[1] + 1)

@app.route('/logout')
@login_required
def logout():
    logout_user() # ログアウト
    return redirect(url_for('login'))

def confirm_match_password(password, confirm_password) -> bool:
    return True if password == confirm_password else False

def judge_commissioner(is_commissioner) -> bool:
    return True if is_commissioner == 'True' else False

if __name__ == '__main__':
    app.run(debug=True)