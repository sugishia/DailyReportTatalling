from flask import request, redirect, render_template, url_for, session
from flask_migrate import current
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user
from flask_login.utils import confirm_login
from models import db, DailyReport, Branch, Branch_Report_Status, Branch_Report_Totals
from app import app, login_manager

from datetime import datetime
import calendar
import sqlite3
import pandas as pd

@login_manager.user_loader
def load_user(branch_id):
    return Branch.query.get(int(branch_id))

@app.errorhandler(401)
def redirect_login(error):
    return render_template('login.html', error='ログインしてください'), 401

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_name = request.form.get('login_name')
        password = request.form.get('password')

        branch = Branch.query.filter_by(login_name=login_name).first()
        #print(branch.branch_name)
        if branch and check_password_hash(branch.password, password):
            login_user(branch)
            session['login_id'] = branch.id
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

@app.route('/report_total', methods=['GET'])
@login_required
def report_total():
    branch = Branch.query.get(session['login_id'])
    if not branch.is_commissioner:
        return render_template('display.html')
    return render_template('report_total.html')

@app.route('/display', methods=['GET', 'POST'])
@login_required
def display():
    if request.method == 'GET':
        report_total = Branch_Report_Totals.query.filter_by(branch_id=session['login_id']).first()
        branch_status = Branch_Report_Status.query.filter_by(branch_id=session['login_id']).first()
        print(branch_status)
        if report_total != None:
            total_list = {'in_party':report_total.in_party, 'out_party':report_total.out_party, 'standing':report_total.standing,
            'leaf_m': report_total.leaf_m, 'leaf_a': report_total.leaf_a, 'dialogue': report_total.dialogue,
            'support': report_total.support, 'workon_join': report_total.workon_join, 'join': report_total.join,
            'akahata_h': report_total.akahata_h, 'akahata_n': report_total.akahata_n, 'support_member': report_total.support_member,
            'ask_favor': report_total.ask_fover}
            status_list = {'is_debate': branch_status.is_debate}
            return render_template('display.html', total_list=total_list, status_list=status_list)
            #return render_template('display.html', total_list=total_list)
        else:
            return render_template('nodata.html')    

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

        is_debate = False
        if request.form['discuss'] == 'True':
            is_debate = True

        print(f'date:{date}, in_party:{in_party}, out_party:{out_party}, readed:{readed}, discuss:{is_debate}')
        with db.session.begin(subtransactions=True):
            branch_id = session.get('login_id')
            new_report = DailyReport(date, in_party, out_party, readed, branch_id, is_debate)
            db.session.add(new_report)
            
            status = Branch_Report_Status.query.filter_by(branch_id=session['login_id']).first()
            if status == None:
                new_statuses = Branch_Report_Status(is_debate, session['login_id'])
                db.session.add(new_statuses)
            else:
                status.is_debate = is_debate
        db.session.commit()
        
        with db.session.begin(subtransactions=True):
            branch_report_total = Branch_Report_Totals.query.filter_by(branch_id=session['login_id']).first()
            print(branch_report_total)
            if branch_report_total == None:
                new_branch_report_total = Branch_Report_Totals(in_party, out_party, readed, session['login_id'])
                db.session.add(new_branch_report_total)
            else:
                #df_sum = df.sum()
                branch_report_total.in_party_total += int(in_party)
                branch_report_total.out_party_total += int(out_party)
                branch_report_total.readed_total += int(readed)

        db.session.commit()
        return redirect(url_for('display'))

    #get
    branch_status = Branch_Report_Status.query.filter_by(branch_id=session['login_id']).first()
    is_debate = False
    if branch_status != None and :
        is_debate = False
    return render_template('report.html', is_reported=is_debate, today={'month':today.month, 'day':today.day}, days=calendar.monthrange(today.year, today.month)[1] + 1)

@app.route('/logout')
@login_required
def logout():
    logout_user() # ログアウト
    session.pop('login_id', None)
    return redirect(url_for('login'))

def sum_result(db_listdata):
    sum = {'in_party':0, 'out_party':0, 'readed':0}
    for data in db_listdata:
        print(f'in_function: inparty = {data}')
        sum['in_party'] += data.in_party
        sum['out_party'] += data.out_party
        sum['readed'] += data.readed
    return sum

def judge_commissioner(is_commissioner) -> bool:
    return True if is_commissioner == 'True' else False

if __name__ == '__main__':
    app.run(debug=True)