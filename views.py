from flask import request, redirect, render_template, url_for, session, jsonify
from flask_migrate import current
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user
from flask_login.utils import confirm_login
from models import db, DailyReport, Branch, Branch_Report_Status, Branch_Report_Totals
from app import app, login_manager
from sqlalchemy import desc

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
            if branch.is_commissioner:
                return redirect(url_for('display_admin'))
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

@app.route('/display_admin', methods=['GET', 'POST'])
@login_required
def display_admin():
    return render_template('display_admin.html')

@app.route('/display', methods=['GET', 'POST'])
@login_required
def display():
    if request.method == 'GET':
        report_detail = DailyReport.query.filter_by(branch_id=session['login_id']).order_by(desc(DailyReport.created_at)).first()
        report_total = Branch_Report_Totals.query.filter_by(branch_id=session['login_id']).first()
        branch_status = Branch_Report_Status.query.filter_by(branch_id=session['login_id']).first()

        print(type(report_detail.date), report_detail.date.year)
        report_detail.date = f'{report_detail.date.year}年{report_detail.date.month}月{report_detail.date.day}日'

        if report_total != None:
            report_list = {'date':report_detail.date, 'in_party':report_detail.in_party, 'out_party':report_detail.out_party, 'standing':report_detail.standing,
            'leaf_m': report_detail.leaf_m, 'leaf_a': report_detail.leaf_a, 'dialogue': report_detail.dialogue,
            'support': report_detail.support, 'workon_join': report_detail.workon_join, 'join': report_detail.join,
            'akahata_h': report_detail.akahata_h, 'akahata_n': report_detail.akahata_n, 'support_member': report_detail.support_member,
            'ask_favor': report_detail.ask_favor, 'comment':report_detail.comment}

            total_list = {'in_party':report_total.in_party, 'out_party':report_total.out_party, 'standing':report_total.standing,
            'leaf_m': report_total.leaf_m, 'leaf_a': report_total.leaf_a, 'dialogue': report_total.dialogue,
            'support': report_total.support, 'workon_join': report_total.workon_join, 'join': report_total.join,
            'akahata_h': report_total.akahata_h, 'akahata_n': report_total.akahata_n, 'support_member': report_total.support_member,
            'ask_favor': report_total.ask_favor}
            status_list = {'is_debate': branch_status.is_debate}
            return render_template('display.html', report_list=report_list, total_list=total_list, status_list=status_list)
            #return render_template('display.html', total_list=total_list)
        else:
            return render_template('nodata.html')    

@app.route('/report_admin', methods=['GET', 'POST'])
@login_required
def report_admin():
    today = datetime.now()
    if request.method == 'POST':

        branch_id = request.form['branch_name']
        #
        month = request.form['month']
        day = request.form['day']
        date = datetime.strptime(f'{datetime.now().year}/{month}/{day}', '%Y/%m/%d')

        in_party = request.form['in_party']
        out_party = request.form['out_party']

        try:
            is_debate = False
            if request.form['discuss'] == 'True':
                is_debate = True
        except Exception as e:
            is_debate = True
        
        standing = request.form['standing']
        leaf_m = request.form['leaf_m']
        leaf_a = request.form['leaf_a']
        dialogue = request.form['dialogue']
        support = request.form['support']

        workon_join = request.form['workon_join']
        join = request.form['join']
        akahata_h = request.form['akahata_h']
        akahata_n = request.form['akahata_n']
        support_member = request.form['support_member']
        ask_fover = request.form['ask_fover']
        comment = request.form['comment']

        #print(f'date:{date}, in_party:{in_party}, out_party:{out_party}, readed:{readed}, discuss:{is_debate}')
        with db.session.begin(subtransactions=True):
            new_report = DailyReport(date, in_party, out_party, standing, leaf_m, leaf_a,
            dialogue, support, workon_join, join, akahata_h, akahata_n, support_member, ask_fover, comment, branch_id)
            db.session.add(new_report)
            
            status = Branch_Report_Status.query.filter_by(branch_id=branch_id).first()
            if status == None:
                new_statuses = Branch_Report_Status(is_debate, branch_id)
                db.session.add(new_statuses)
            else:
                status.is_debate = is_debate
        db.session.commit()
        
        with db.session.begin(subtransactions=True):
            branch_report_total = Branch_Report_Totals.query.filter_by(branch_id=branch_id).first()
            print(branch_report_total)
            if branch_report_total == None:
                new_branch_report_total = Branch_Report_Totals(date, in_party, out_party, standing, leaf_m, leaf_a,
                dialogue, support, workon_join, join, akahata_h, akahata_n, support_member, ask_fover, branch_id)
                db.session.add(new_branch_report_total)
            else:
                branch_report_total.date = date
                branch_report_total.in_party += int(in_party)
                branch_report_total.out_party += int(out_party)
                branch_report_total.standing += int(standing)
                branch_report_total.leaf_m += int(leaf_m)
                branch_report_total.leaf_a += int(leaf_a)
                branch_report_total.dialogue += int(dialogue)
                branch_report_total.support += int(support)
                branch_report_total.workon_join += int(workon_join)
                branch_report_total.join += int(join)
                branch_report_total.akahata_h += int(akahata_h)
                branch_report_total.akahata_n += int(akahata_n)
                branch_report_total.support_member += int(support_member)
                branch_report_total.ask_favor += int(ask_fover)
                branch_report_total.branch_id = branch_id

        db.session.commit()
        return redirect(url_for('display_admin'))

    #get
    branches = Branch.query.filter(Branch.login_name != 'admin').all()
    print(branches)
    return render_template('report_admin.html', today={'month':today.month, 'day':today.day}, days=calendar.monthrange(today.year, today.month)[1] + 1, branches=branches)

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    today = datetime.now()
    if request.method == 'POST':

        #
        month = request.form['month']
        day = request.form['day']
        date = datetime.strptime(f'{datetime.now().year}/{month}/{day}', '%Y/%m/%d')

        in_party = request.form['in_party']
        out_party = request.form['out_party']

        try:
            is_debate = False
            if request.form['discuss'] == 'True':
                is_debate = True
        except Exception as e:
            is_debate = True
        
        standing = request.form['standing']
        leaf_m = request.form['leaf_m']
        leaf_a = request.form['leaf_a']
        dialogue = request.form['dialogue']
        support = request.form['support']

        workon_join = request.form['workon_join']
        join = request.form['join']
        akahata_h = request.form['akahata_h']
        akahata_n = request.form['akahata_n']
        support_member = request.form['support_member']
        ask_fover = request.form['ask_fover']
        comment = request.form['comment']

        #print(f'date:{date}, in_party:{in_party}, out_party:{out_party}, readed:{readed}, discuss:{is_debate}')
        with db.session.begin(subtransactions=True):
            branch_id = session.get('login_id')
            new_report = DailyReport(date, in_party, out_party, standing, leaf_m, leaf_a,
            #dialogue, support, workon_join, join, akahata_h, akahata_n, support_member, ask_fover, session['login_id'])
            dialogue, support, workon_join, join, akahata_h, akahata_n, support_member, ask_fover, comment, session['login_id'])
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
                new_branch_report_total = Branch_Report_Totals(date, in_party, out_party, standing, leaf_m, leaf_a,
                dialogue, support, workon_join, join, akahata_h, akahata_n, support_member, ask_fover, branch_id)
                db.session.add(new_branch_report_total)
            else:
                branch_report_total.date = date
                branch_report_total.in_party += int(in_party)
                branch_report_total.out_party += int(out_party)
                branch_report_total.standing += int(standing)
                branch_report_total.leaf_m += int(leaf_m)
                branch_report_total.leaf_a += int(leaf_a)
                branch_report_total.dialogue += int(dialogue)
                branch_report_total.support += int(support)
                branch_report_total.workon_join += int(workon_join)
                branch_report_total.join += int(join)
                branch_report_total.akahata_h += int(akahata_h)
                branch_report_total.akahata_n += int(akahata_n)
                branch_report_total.support_member += int(support_member)
                branch_report_total.ask_favor += int(ask_fover)
                branch_report_total.branch_id = branch_id

        db.session.commit()
        return redirect(url_for('display'))

    #get
    branch_status = Branch_Report_Status.query.filter_by(branch_id=session['login_id']).first()
    debate_disable_flag = False
    msg = ''
    #アンケート投稿がある　かつ　討議している
    if branch_status != None and branch_status.is_debate == True:
        msg = '(報告済み)'
        debate_disable_flag = True
    return render_template('report.html', msg = msg, debate_disable_flag=debate_disable_flag, today={'month':today.month, 'day':today.day}, days=calendar.monthrange(today.year, today.month)[1] + 1)

@app.route('/logout')
@login_required
def logout():
    logout_user() # ログアウト
    session.pop('login_id', None)
    return redirect(url_for('login'))

@app.route('/ajax', methods=['POST'])
def ajax_return():
    if request.method == 'POST':
        val1 = int(request.form['val'])
        #print(val1, type(val1))
        branch_status = Branch_Report_Status.query.filter_by(branch_id=val1).first()
        if branch_status != None and branch_status.is_debate == True:
            return jsonify({'result': True})
        return jsonify({'result': False})
    #return jsonify({'test': 'test'})

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