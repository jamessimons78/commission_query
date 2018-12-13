# 作者：Qingzhao Ming
# E-mail: Jamessimons78@163.com

import sqlite3
from flask import Flask, render_template, g, request, session, url_for, redirect, flash, abort
from config import DevConfig

app = Flask(__name__)
app.config.from_object(DevConfig)

def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    account = request.form['account']
    password = request.form['password']
    get_db()
    cur = g.db.execute("select commission_account from user where commission_account==? and commission_password ==?", [account, password])
    row = cur.fetchone()

    if not row:
        error = '您输入的账号或密码有误，或系统里还没有您的佣金账号！'
    elif account == row[0]:
        session['logged_in'] = True
        session['account'] = account
        flash('您已经成功登录佣金查询系统！')
        return redirect(url_for('show_base_information'))
    return render_template('login.html', error=error)

@app.route('/show_base_information')
def show_base_information():
    if not session.get('logged_in'):
        abort(401)
    account = session['account']
    get_db()
    cur = g.db.execute("select name from user where referrer_account==?", [account])
    rows = cur.fetchall()
    clients = [row[0] for row in rows]
    return render_template('base_information.html', clients=clients)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('account', None)
    flash('您已经安全退出查询系统！')
    return render_template('login.html')

if __name__ == '__main__':
    app.run()