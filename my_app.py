# 作者：Qingzhao Ming
# E-mail: Jamessimons78@163.com

from datetime import datetime
import re
import sqlite3
from flask import Flask, render_template, g, request, session, url_for, redirect, flash, abort
from config import DevConfig


app = Flask(__name__)
app.config.from_object(DevConfig)


def connect_db():
    '''
    连接数据库
    '''
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def get_db():
    '''
    需要用数据库时，先检查全局变量g中是否有数据库连接，若没有则连接数据库
    '''
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


@app.teardown_appcontext
def close_db(error):
    '''
    应用环境销毁时调用关闭数据库连接
    '''
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def index():
    '''
    首页直接登录
    '''
    return render_template('login.html')


@app.route('/login', methods=['GET','POST'])
def login():
    '''
    登录界面
    '''
    account = request.form['account']
    password = request.form['password']
    account_reg = r'^[1-9]\d+$'
    if not re.match(account_reg, account):
        rule = False
        error = '您输入的经纪人账号不符合MT4账号的规则，请核实后再录入！'
    elif len(password)==0:
        rule = False
        error = '需要输入密码才能登录！'
    else:
        get_db()
        cur = g.db.execute("select commission_account, manager from user where commission_account==? and password ==?", [account, password])
        row = cur.fetchone()

        if not row:
            error = '您输入的账号或密码有误，或系统里还没有您的佣金账号！'
        elif account == row[0]:
            session['logged_in'] = True
            session['account'] = account
            # 普通代理登录
            if row[1] == 0:
                flash('您已经成功登录——佣金查询系统！')
                return redirect(url_for('show_base_information'))
            # 管理员登录
            elif row[1] == 1:
                flash('您已经登录——后台管理系统！')
                return redirect(url_for('back_stage_management'))
    return render_template('login.html', error=error)


@app.route('/show_base_information')
def show_base_information():
    '''
    显示代理自己名下的客户列表基本信息
    '''
    if not session.get('logged_in'):
        abort(401)
    account = session['account']
    get_db()
    cur = g.db.execute("select ib_name from user where referrer_account==?", [account])
    rows = cur.fetchall()
    clients = [row[0] for row in rows]
    return render_template('base_information.html', clients=clients)


@app.route('/commission_query')
def commission_query():
    '''
    代理查询自己的返佣情况
    '''
    pass


@app.route('/back_stage_management')
def back_stage_management():
    '''
    后台管理：添加代理资料、输入每周交易量及每月盈利分红
    '''
    return render_template('back_stage_management.html')


@app.route('/add_ib')
def add_ib():
    '''
    后台管理：添加经纪人资料
    '''
    if not session.get('logged_in'):
        abort(401)

    # 初始化输入控件
    ib_info = {}
    ib_info['ib_name'] = ''
    ib_info['commission_account'] = ''
    ib_info['password'] = ''
    ib_info['investment_account'] = ''
    ib_info['referrer_account'] = ''
    ib_info['referrer_name'] = ''

    return render_template('add_ib.html', ib_info=ib_info)


@app.route('/add_ib_submit', methods=['GET','POST'])
def add_ib_submit():
    ib_name = request.form['ib_name']
    commission_account = request.form['commission_account']
    password = request.form['password']
    investment_account = request.form['investment_account']
    referrer_account = request.form['referrer_account']
    referrer_name = request.form['referrer_name']

    rule = True
    if len(ib_name) == 0 or (len(commission_account) > 0 and len(password) == 0) \
            or (len(commission_account) == 0 and len(password) > 0) \
            or (len(commission_account) == 0 and len(investment_account) == 0) \
            or len(referrer_account) == 0:
        rule = False
        error = '您输入的经纪人资料有误，关键信息不能为空！'
    else:
        name_reg = r'^[A-Za-z][A-Za-z\s]+$'
        if not re.match(name_reg, ib_name):
            rule = False
            error = '您输入的姓名格式不对，请输入拼音！'

        account_reg = r'^[1-9]\d+$'
        if rule and len(commission_account)>0:
            if not re.match(account_reg, commission_account):
                rule = False
                error = '您输入的经纪人佣金账号不符合MT4账号的规则，请核实后再录入！'

        if rule and len(password) > 0:
            password_reg = r'^[A-Za-z0-9]+$'
            if not re.match(password_reg, password):
                rule = False
                error = '您输入的密码格式不对，请输入拼音！'

        if rule and len(investment_account)>0:
            if not re.match(account_reg, investment_account):
                rule = False
                error = '您输入的投资账号不符合MT4账号的规则，请核实后再录入！'

        if rule and not re.match(account_reg, referrer_account):
            rule = False
            error = '您输入的推荐人账号不符合MT4账号的规则，请核实后再录入！'
        
        if rule and len(commission_account) > 0:
            get_db()
            cur = g.db.execute("select commission_account from user where commission_account==?", [commission_account])
            row = cur.fetchone()
            if row:
                rule = False
                error = '您输入的经纪人账号与系统里的重复了，请核实后再录入！'

        if rule and len(referrer_account) > 0:
            get_db()
            cur = g.db.execute("select commission_account from user where commission_account==?", [referrer_account])
            row = cur.fetchone()
            if not row:
                rule = False
                error = '系统里没有您输入的推荐人账号，请核实后再录入！'

    if rule:
        dt = datetime.now()
        input_date = dt.strftime("%Y-%m-%d")
        inputer = session.get('account')
        # get_db()
        g.db.execute('insert into user (ib_name, commission_account, password, investment_account, referrer_account, referrer_name, input_date, inputer) '
                     'values (?, ?, ?, ?, ?, ?, ? ,?)', [ib_name, commission_account, password, investment_account, referrer_account, referrer_name, input_date, inputer])
        g.db.commit()

        flash('你已经成功添加了一个新经纪人的资料')
        return redirect(url_for('add_ib'))
    else:
        # 当输入有误时，将原有输入内容传入新的输入页面
        ib_info = {}
        ib_info['ib_name'] = ib_name
        ib_info['commission_account'] = commission_account
        ib_info['password'] = password
        ib_info['investment_account'] = investment_account
        ib_info['referrer_account'] = referrer_account
        ib_info['referrer_name'] = referrer_name
        return render_template('add_ib.html', error=error, ib_info=ib_info)


@app.route('/entering_vol', methods=['GET','POST'])
def entering_vol():
    '''
    后台管理：输入上周交易量
    '''
    pass


@app.route('/entering_dividend', methods=['GET','POST'])
def entering_dividend():
    '''
    后台管理：输入上月盈利分红
    '''
    pass


@app.route('/logout')
def logout():
    '''
    退出时删除会话中的相关全局变量
    '''
    session.pop('logged_in', None)
    session.pop('account', None)
    flash('您已经安全退出查询系统！')
    return render_template('login.html')


if __name__ == '__main__':
    app.run()