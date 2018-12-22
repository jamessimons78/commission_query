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
    # 初始化输入控件
    account = ''
    return render_template('login.html', account=account)


@app.route('/login', methods=['GET','POST'])
def login():
    '''
    登录界面
    '''
    account = request.form['account']
    password = request.form['password']
    if len(account) > 0 and len(password) > 0:
        account_reg = r'^[1-9]\d+$'
        if not re.match(account_reg, account):
            error = '您输入的经纪人账号不符合MT4账号的规则，请核实后再录入！'
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
    else:
        error = 'MT4佣金账号，或密码不能为空！'
    
    return render_template('login.html', error=error, account=account)


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


@app.route('/show_detail_information')
def show_detail_information():
    '''
    代理查询自己的返佣详细情况
    '''
    if not session.get('logged_in'):
        abort(401)
    
    account = session['account']
    get_db()
    # 查询上周交易量及佣金
    cur = g.db.execute('SELECT commission.investment_account, user.ib_name, commission.trading_vol, commission.commission_points, commission.commission '
                       'FROM commission LEFT JOIN user ON user.investment_account = commission.investment_account '
                       'WHERE (commission.referrer_account==? AND commission.input_date==(SELECT MAX(commission.input_date) FROM commission))', [account])
    rows = cur.fetchall()
    # 将查询结果用last_week列表变量传给网页
    last_week = [[row[0], row[1], row[2], row[3], row[4]] for row in rows]
    # 佣金小计和总计
    commission = [0, 0]
    for row in rows:
        commission[0] += row[4]
    commission[0] = round(commission[0], 2)

    # 查询总交易量及佣金
    cur = g.db.execute('SELECT commission.investment_account, user.ib_name, sum(commission.trading_vol), commission.commission_points, sum(commission.commission) '
                       'FROM commission LEFT JOIN user ON user.investment_account = commission.investment_account '
                       'WHERE commission.referrer_account==? GROUP BY commission.investment_account', [account])
    rows = cur.fetchall()
    all = [[row[0], row[1], row[2], row[3], row[4]] for row in rows]
    for row in rows:
        commission[1] += row[4]
    commission[1] = round(commission[1], 2)

    # 查询截止日期
    cur = g.db.execute('SELECT MAX(input_date) FROM trading_vol')
    row = cur.fetchone()
    expiration_date = row[0]

    return render_template('detail_information.html', last_week=last_week, all=all, commission=commission, expiration_date=expiration_date)


@app.route('/back_stage_management')
def back_stage_management():
    '''
    后台管理：添加代理资料、输入每周交易量及每月盈利分红
    '''
    if not session.get('logged_in'):
        abort(401)

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
    if not session.get('logged_in'):
        abort(401)

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
        error = '关键信息不能为空！'
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
        g.db.execute('insert into user (ib_name, commission_account, password, investment_account, referrer_account, referrer_name, input_date, inputer) values (?, ?, ?, ?, ?, ?, ? ,?)', [ib_name, commission_account, password, investment_account, referrer_account, referrer_name, input_date, inputer])
        g.db.commit()

        if len(investment_account) > 0:
            flash('已添加 ' + ib_name + ' 的资料，现在设置相关推荐人的佣金点数')
            session['investment_account'] = investment_account
            return redirect(url_for('commission_points_setting'))
        else:
            flash('已添加 ' + ib_name + ' 的资料')
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


@app.route('/commission_points_setting', methods=['GET','POST'])
def commission_points_setting():
    '''
    添加经纪人或客户账号后，设置相关推荐人的佣金点数
    '''
    if not session.get('logged_in'):
        abort(401)

    # 获取本次添加的投资账号的所有相关推荐人的账号
    investment_account = session.get('investment_account')
    referrer_account = get_referrer_account(investment_account)
    
    # 获取推荐人账号对应的姓名
    referrers = get_referrers(referrer_account)
    
    return render_template('commission_points.html', referrers=referrers)


@app.route('/commission_points_setting_submit', methods=['GET','POST'])
def commission_points_setting_submit():
    '''
    添加经纪人或客户账号后，设置相关推荐人的佣金点数
    '''
    if not session.get('logged_in'):
        abort(401)

    investment_account = session.get('investment_account')
    referrer_accounts = get_referrer_account(investment_account)

    rule = True
    points_reg = r'^(([1-9]{1})|([1]{1}[0-8]{1})|([0-9]{1}\.[0-9][1-9]?)|([1]{1}[0-7]{1}\.[0-9][1-9]?))$'
    commission_points = []
    for referrer in referrer_accounts:
        points = request.form[referrer]
        commission_points.append(points)
        if rule and len(points) > 0:
            if not re.match(points_reg, points):
                rule = False
                error = '您输入的佣金点数(美金/手)不符合要求，请核实后再录入！'
    if rule and len(commission_points[0]) == 0:
        rule = False
        error = '直接推荐人的佣金点数必须设置！'
    if rule:
        s = 0
        for points in commission_points:
            if len(points) > 0:
                s += float(points)
        if s > 18:
            rule = False
            error = '佣金点数设置错误，总数已超18美金/手！'
    
    if rule:
        dt = datetime.now()
        input_date = dt.strftime("%Y-%m-%d")
        inputer = session.get('account')

        for i in range(len(referrer_accounts)):
            if len(commission_points[i]) > 0:
                g.db.execute('insert into commission_points (investment_account, referrer_account, commission_points, input_date, inputer) '
                             'values (?, ?, ?, ?, ?)', [investment_account, referrer_accounts[i], commission_points[i], input_date, inputer])
                g.db.commit()
        
        session.pop('investment_account', None)
        flash('已添加 ' + investment_account + '，并设置了推荐人佣金点数')
        return redirect(url_for('add_ib'))
    else:
        referrers = get_referrers(referrer_accounts)
        return render_template('commission_points.html', error=error, referrers=referrers)


def get_referrer_account(investment_account):
    '''
    获取指定投资账号的所有相关推荐人的账号
    '''
    get_db()
    cur = g.db.execute('select referrer_account from user where investment_account==?', [investment_account])
    row = cur.fetchone()
    referrer_account = []
    referrer_account.append(row[0])
    a = row[0]
    for i in range(5):
        cur = g.db.execute('select referrer_account from user where commission_account==?', [a])
        row = cur.fetchone()
        if row[0] is not None:
            referrer_account.append(row[0])
            a = row[0]
        else:
            break
    return referrer_account


def get_referrers(referrer_account):
    '''
    获取指定推荐人账号对应的姓名
    '''
    referrers = []
    get_db()
    for a in referrer_account:
        cur = g.db.execute('select commission_account, ib_name from user where commission_account==?', [a])
        row = cur.fetchone()
        referrers.append(dict(account=row[0], name=row[1]))
    return referrers


@app.route('/entering_vol')
def entering_vol():
    '''
    后台管理：输入上周交易量
    '''
    if not session.get('logged_in'):
        abort(401)

    # 初始化输入控件
    vol_dict = {}
    vol_dict['investment_account'] = ''
    vol_dict['trading_vol'] = ''

    return render_template('entering_vol.html', vol_dict=vol_dict)


@app.route('/entering_vol_submit', methods=['GET','POST'])
def entering_vol_submit():
    if not session.get('logged_in'):
        abort(401)

    investment_account = request.form['investment_account']
    trading_vol = request.form['trading_vol']

    rule = True
    if len(investment_account) == 0 or len(trading_vol) == 0:
        rule = False
        error = '不能提交空的数据！'
    else:
        account_reg = r'^[1-9]\d+$'
        if not re.match(account_reg, investment_account):
            rule = False
            error = '您输入的投资账号不符合MT4账号的规则，请核实后再录入！'
        
        if rule:
            vol_reg = r'^[0-9]{0,3}[.][0-9]{2}$'
            if not re.match(vol_reg, trading_vol):
                rule = False
                error = '您输入的交易量不符合规则，请核实后再录入！'

        if rule:
            get_db()
            cur = g.db.execute("select investment_account from user where investment_account==?", [investment_account])
            row = cur.fetchone()
            if not row:
                rule = False
                error = '系统里没有您输入的MT4投资账号，请核实后再录入！'

        if rule:
            dt = datetime.now()
            input_date = dt.strftime("%Y-%m-%d")
            get_db()
            cur = g.db.execute("select investment_account from trading_vol where investment_account==? and input_date==?", [investment_account, input_date])
            row = cur.fetchone()
            if row:
                rule = False
                error = '该账号今天已录入过交易量，请核实后再录入！'

    vol_dict = {}
    vol_dict['investment_account'] = investment_account
    vol_dict['trading_vol'] = trading_vol

    if rule:
        session['investment_account'] = investment_account
        session['trading_vol'] = trading_vol
        error = '以下数据是否正确，确定要提交？'
        return render_template('entering_vol_confirm.html', error=error, vol_dict=vol_dict)

    else:
        # 当输入有误时，将原有输入内容传入新的输入页面
        return render_template('entering_vol.html', error=error, vol_dict=vol_dict)


@app.route('/entering_vol_confirm', methods=['GET','POST'])
def entering_vol_confirm():
    if not session.get('logged_in'):
        abort(401)

    investment_account = session.get('investment_account')
    trading_vol = session.get('trading_vol')
    session.pop('investment_account', None)
    session.pop('trading_vol', None)

    dt = datetime.now()
    input_date = dt.strftime("%Y-%m-%d")
    inputer = session.get('account')
    get_db()
    # 添加交易量到trading_vol表中
    g.db.execute('insert into trading_vol (investment_account, trading_vol, input_date, inputer) '
                 'values (?, ?, ?, ?)', [investment_account, trading_vol, input_date, inputer])
    g.db.commit()

    # 查询该投资账号有哪些推荐人以及相应的佣金点数
    cur = g.db.execute("select referrer_account, commission_points from commission_points where investment_account==?", [investment_account])
    rows = cur.fetchall()
    # 添加佣金到commission表中，每一级推荐人都相应的添加
    for row in rows:
        referrer_account = row[0]
        commission_points = row[1]
        commission = round(float(trading_vol) * commission_points, 2)
        g.db.execute('insert into commission (investment_account, trading_vol, referrer_account, commission_points, commission, input_date, inputer) '
                     'values (?, ?, ?, ?, ?, ?, ?)', [investment_account, trading_vol, referrer_account, commission_points, commission, input_date, inputer])
        g.db.commit()

    flash('已添加账号 ' + investment_account + ' 的交易量，和各级推荐人的佣金')
    return redirect(url_for('entering_vol'))
    

@app.route('/entering_dividend')
def entering_dividend():
    '''
    后台管理：输入上月盈利分红
    '''
    if not session.get('logged_in'):
        abort(401)

    # 初始化输入控件
    dividend_dict = {}
    dividend_dict['investment_account'] = ''
    dividend_dict['dividend'] = ''

    return render_template('entering_dividend.html', dividend_dict=dividend_dict)


@app.route('/entering_dividend_submit', methods=['GET','POST'])
def entering_dividend_submit():
    if not session.get('logged_in'):
        abort(401)

    investment_account = request.form['investment_account']
    dividend = request.form['dividend']

    rule = True
    if len(investment_account) == 0 or len(dividend) == 0:
        rule = False
        error = '不能提交空的数据！'
    else:
        account_reg = r'^[1-9]\d+$'
        if not re.match(account_reg, investment_account):
            rule = False
            error = '您输入的投资账号不符合MT4账号的规则，请核实后再录入！'
        
        if rule:
            dividend_reg = r'^[0-9]{0,5}[.][0-9]{2}$'
            if not re.match(dividend_reg, dividend):
                rule = False
                error = '您输入的分红不符合规则，请核实后再录入！'

        if rule:
            get_db()
            cur = g.db.execute("select investment_account from user where investment_account==?", [investment_account])
            row = cur.fetchone()
            if not row:
                rule = False
                error = '系统里没有您输入的MT4投资账号，请核实后再录入！'

        if rule:
            dt = datetime.now()
            input_date = dt.strftime("%Y-%m-%d")
            get_db()
            cur = g.db.execute("select investment_account from dividend where investment_account==? and input_date==?", [investment_account, input_date])
            row = cur.fetchone()
            if row:
                rule = False
                error = '该账号今天已录入过分红，请核实后再录入！'

    if rule:
        inputer = session.get('account')
        # get_db()
        g.db.execute('insert into dividend (investment_account, dividend, input_date, inputer) '
                     'values (?, ?, ?, ?)', [investment_account, dividend, input_date, inputer])
        g.db.commit()

        flash('已添加账号 ' + investment_account + ' 的分红')
        return redirect(url_for('entering_dividend'))
    else:
        # 当输入有误时，将原有输入内容传入新的输入页面
        dividend_dict = {}
        dividend_dict['investment_account'] = investment_account
        dividend_dict['dividend'] = dividend
        return render_template('entering_dividend.html', error=error, dividend_dict=dividend_dict)
    

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