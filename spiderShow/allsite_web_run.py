#!/usr/bin/env python
# coding=utf-8
import re
import os
import urlparse
import redis
import json
import datetime
import dedup
import MySQLdb
import subprocess
from flask import Flask, render_template, request, url_for, flash, redirect
from flask import send_from_directory
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import validators
from wtforms import FieldList, IntegerField, StringField, RadioField, DecimalField, DateTimeField, \
    FormField, SelectField, TextField, PasswordField, TextAreaField, BooleanField, SubmitField
from werkzeug.datastructures import MultiDict
from werkzeug.utils import secure_filename

#
# import sys
# sys.path.append(r'')
# import

app = Flask(__name__)
app.config['SECRET_KEY'] = 'success'
app.config['EXPORT_FOLDER'] = 'static/export/'
bootstrap = Bootstrap(app)

redis_setting = 'redis://127.0.0.1/14'
dedup_setting = 'redis://192.168.110.110/0'
PROCESS_SHOW_JSON = "process_show_temp.json"
EXPORT_FOLDER = 'static/export/'

# RUN_PY_FILE = "run_spider.bat"
if os.name == 'nt':
    RUN_PY_FILE = 'D:\workspace\pyWorks\spider\\allsite_url_rule_manual.py'
else:
    RUN_PY_FILE = '/Users/song/workspace/pyWorks/spider/allsite_url_rule_manual.py'


# def is_me(form, field): #自定义check函数
#     if field.data != 'yes':
#         raise validators.ValidationError('Must input "yes"') #FormField对象
#
# class addressForm(Form):
#     city = IntegerField('city', [validators.required()])
#     area = IntegerField('area', [validators.required()])
#     building = StringField('building')
#
#
# class InputForm(Form):
#     me = StringField('Is your self info?',[is_me,validators.Length(min=1,max=3)])
#     name = StringField('What is your name?',
#                        [validators.InputRequired('name'),
#                        validators.Regexp('\w+', message="Must contain 0-9 aA-zZ")],
#                        description='must input your name.',default=u'songyq')
#     birthday  = DateTimeField('Your Birthday', format='%m/%d/%y')
#     sex  = RadioField('Sex', choices=[(1,'man'),(2,'women')])
#     age = DecimalField('How old are you?',
#                        [validators.DataRequired('must be number!'),
#                         validators.NumberRange(min=10, max=100, message='10~100')],
#                        description='must input your age.')
#     national = SelectField('national', choices=[('cn', 'china'), ('en', 'usa'), ('jp', 'japan')])
#     address1 = TextAreaField('Address1', [validators.optional(), validators.length(max=200)])
#     address2 = FormField(addressForm)
#     phone = IntegerField('What is your phone number?',
#                          [validators.InputRequired('phone')],
#                          description='must input your phone.')
#     password = PasswordField('New Password',
#                              [validators.Required()])
#     confirm = PasswordField('Repeat Password',
#                             [validators.Required(),
#                              validators.EqualTo('password', message='Passwords must match')])
#     accept_tos = BooleanField('singe boy', [validators.Required()])
#     email = TextField('Email Address', [validators.Length(min=6, message=(u'Little short for an email address?')),
#                                         validators.Email(message=(u'That\'s not a valid email address.'))])
#     submit = SubmitField('Submit')

class RegexForm(Form):
    select = BooleanField(label=u'选择', default=False)
    regex = StringField(label=u'表达式')  # , default='/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
    weight = SelectField(label=u'权重', choices=[('100', u'确定'), ('50', u'可能'), ('30', u'。。。')])
    score = IntegerField(label=u'匹配数', default=0)


class DetailUrlForm(Form):
    detail_url = StringField(label=u'详情页')
    select = BooleanField(label=u'正误', default=False)


class ListUrlForm(Form):
    list_url = StringField(label=u'列表页')
    select = BooleanField(label=u'正误', default=False)


class InputForm(Form):
    start_url = StringField(label=u'主页')  # cpt.xtu.edu.cn'  # 湘潭大学
    site_domain = StringField(label=u'限定域名')  # 'http://cpt.xtu.edu.cn/'
    white_list = StringField(label=u'白名单')
    black_list = StringField(label=u'域名黑名单')

    result = StringField(label=u'转换结果')
    convert = SubmitField(label=u'<< 转换')
    url = StringField(label=u'URL例子')

    list_regex_list = FieldList(FormField(RegexForm), label=u'列表页-正则表达式', min_entries=50)

    detail_regex_list = FieldList(FormField(RegexForm), label=u'详情页-正则表达式', min_entries=50)

    reset = BooleanField(label=u'将原有正则表达式的score清零', default=False)

    submit = SubmitField(label=u'保存并执行')

    import_setting = SubmitField(label=u'导入')


class OutputForm(Form):
    show_max = 200

    detail_urls_list = FieldList(FormField(DetailUrlForm), label=u'提取结果一览-详情页', min_entries=show_max)

    list_urls_list = FieldList(FormField(ListUrlForm), label=u'提取结果一览-列表页', min_entries=show_max)

    refresh = SubmitField(label=u'刷新')


class MySqlDrive(object):
    def __init__(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        self.host = 'localhost'
        self.user = 'root'
        self.password = 'root'
        self.port = 3306
        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port,
                                    charset="utf8")
        self.conn.select_db('spider')
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def save_all_setting(self, start_url, site_domain, setting_json, detail_regex_save_list,
                         list_regex_save_list):
        # print 'save_to_mysql() start...', start_url, site_domain

        ret_cnt = 0
        try:
            sqlStr1 = (
                "DELETE FROM url_rule WHERE start_url= '" + start_url + "' AND site_domain= '" + site_domain + "'")
            self.cur.execute(sqlStr1)
            self.conn.commit()

            # detail_or_list = '0'  # 0:detail,1:list
            # scope = '0'           # 0:netloc,1:path,2:query
            # white_or_black = '0'  # 0:white,1:black
            # weight = '0'          # 100:高，50：中，20：低

            for regex, weight in detail_regex_save_list:
                detail_or_list = '0'
                scope = '1'
                white_or_black = '0'
                sqlStr2 = "INSERT INTO url_rule(start_url,site_domain,detail_or_list, scope,white_or_black,weight,regex) " \
                          "VALUES ('" + start_url + "','" + site_domain + "','" + detail_or_list + "','" + \
                          scope + "','" + white_or_black + "','" + weight + "','" + regex + "')"
                # print 'save_to_mysql() detail', sqlStr2
                ret_cnt = self.cur.execute(sqlStr2)
                self.conn.commit()

            for regex, weight in list_regex_save_list:
                detail_or_list = '1'
                scope = '1'
                white_or_black = '0'
                sqlStr2 = "INSERT INTO url_rule(start_url,site_domain,detail_or_list, scope,white_or_black,weight,regex) " \
                          "VALUES ('" + start_url + "','" + site_domain + "','" + detail_or_list + "','" + \
                          scope + "','" + white_or_black + "','" + weight + "','" + regex + "')"
                # print 'save_to_mysql() list', sqlStr2
                ret_cnt = self.cur.execute(sqlStr2)
                self.conn.commit()

        except Exception, e:
            print '[ERROR]save_to_mysql()', e
            self.conn.rollback()

        return ret_cnt

    def get_current_main_setting(self):
        # 提取主页、域名
        start_url = ''
        site_domain = ''
        sqlStr = "SELECT * FROM current_main_setting"
        try:
            cnt = self.cur.execute(sqlStr)
            if cnt == 1:
                (id, start_url, site_domain, setting_json) = self.cur.fetchone()
                self.conn.commit()
            # print 'get_current_main_setting()', cnt, sqlStr
        except Exception, e:
            print 'get_current_main_setting()', e

        return start_url, site_domain  # , setting_json

    def set_current_main_setting(self, start_url, site_domain, setting_json):
        # 提取主页、域名
        sqlStr1 = "DELETE FROM current_main_setting"
        sqlStr2 = "INSERT INTO current_main_setting(start_url,site_domain,setting_json) " \
                  "VALUES ('" + start_url + "','" + site_domain + "','" + setting_json + "')"
        try:
            # print 'set_current_main_setting()', sqlStr1
            self.cur.execute(sqlStr1)
            # print 'set_current_main_setting()', sqlStr2
            cnt = self.cur.execute(sqlStr2)
            self.conn.commit()
        except Exception, e:
            print '[ERROR]set_current_main_setting()', e, sqlStr1
            print '[ERROR]set_current_main_setting()', e, sqlStr2

        return start_url, site_domain, setting_json

    def clean_current_main_setting(self):
        # 提取主页、域名
        sqlStr = "DELETE FROM current_main_setting"
        try:
            self.cur.execute(sqlStr)
            self.conn.commit()
            # print 'get_current_main_setting()', sqlStr
        except Exception, e:
            print '[ERROR]get_current_main_setting()', e

    def get_regexs(self, type):
        # 0:detail,1:list
        if type == 'detail':
            detail_or_list = '0'
        else:
            detail_or_list = '1'
        regexs = []
        # 提取主页、域名
        start_url, site_domain = self.get_current_main_setting()
        sqlStr = "SELECT black_domain,scope,white_or_black,weight,regex,etc FROM url_rule " \
                 "WHERE start_url='" + start_url + "' AND site_domain = '" + site_domain + "' AND detail_or_list='" + detail_or_list + "'"
        try:
            cnt = self.cur.execute(sqlStr)
            rs = self.cur.fetchall()
            for r in rs:
                (black_domain, scope, white_or_black, weight, regex, etc) = r
                regexs.append((black_domain, scope, white_or_black, weight, regex, etc))
            self.conn.commit()
            # print 'get_regexs()', cnt, sqlStr
        except Exception, e:
            print '[ERROR]get_regexs()', e
        return regexs


class RedisDrive(object):
    def __init__(self, start_url, site_domain, redis_setting):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url(redis_setting)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain  # 计算结果
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain  # 计算结果
        self.manual_list_urls_rule_zset_key = 'manual_list_urls_rule_zset_%s' % self.site_domain  # 手工配置规则
        self.manual_detail_urls_rule_zset_key = 'manual_detail_urls_rule_zset_%s' % self.site_domain  # 手工配置规则
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0
        # print 'RedisDrive init()', self.site_domain, self.start_url, self.conn

    def get_detail_urls(self):
        return self.conn.zrangebyscore(self.detail_urls_zset_key, min=self.done_flg, max=self.done_flg)

    def get_list_urls(self):
        return self.conn.zrangebyscore(self.list_urls_zset_key, min=self.todo_flg, max=self.done_flg)

    def get_matched_rate(self):
        cnt = 0
        urls = self.get_detail_urls()
        if len(urls) == 0:
            return 0.0

        de = dedup.Dedup('192.168.110.110', 'dedup')
        for url in urls:
            # if (de.is_dedup(url)):
            #     print 'matched:', url
            #     cnt += 1
            cnt = 1

        return float(cnt) / len(urls)

    def get_keywords_match(self):
        # keywords = "'" + "','".join(['list', 'index', 'detail', 'post', 'content']) + "'"
        keywords = "'" + "','".join(['list', 'index', 'detail', 'post', 'content']) + "'"
        matched_cnt = ','.join(['99', '2', '10', '30', '1'])
        print keywords, matched_cnt
        return keywords, matched_cnt

    def covert_redis_cnt_to_json(self):
        # rule0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        # rule1_cnt = self.conn.zcard(self.detail_urls_rule1_zset_key)
        rule0_cnt = 0
        rule1_cnt = 0
        detail_cnt = self.conn.zcard(self.detail_urls_zset_key)
        list_cnt = self.conn.zcard(self.list_urls_zset_key)
        list_done_urls = self.conn.zrangebyscore(
            self.list_urls_zset_key, self.done_flg, self.done_flg)
        list_done_cnt = len(list_done_urls)
        t_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cnt_info = {'times': t_stamp, 'rule0_cnt': rule0_cnt, 'rule1_cnt': rule1_cnt,
                    'detail_cnt': detail_cnt, 'list_cnt': list_cnt, 'list_done_cnt': list_done_cnt}
        self.conn.hset(
            self.process_cnt_hset_key, t_stamp, json.dumps(cnt_info))
        print cnt_info
        jsonStr = json.dumps(cnt_info)
        fp = open(EXPORT_FOLDER + '/' + PROCESS_SHOW_JSON, 'a')
        fp.write(jsonStr)
        fp.write('\n')
        fp.close()


class CollageProcessInfo(object):
    def __init__(self):
        self.json_file = PROCESS_SHOW_JSON

    def convert_file_to_list(self):
        rule0_cnt = []
        rule1_cnt = []
        detail_cnt = []
        list_cnt = []
        list_done_cnt = []
        times = []

        fp = open(EXPORT_FOLDER + '/' + PROCESS_SHOW_JSON, 'r')
        for line in fp.readlines():
            dic = eval(line)
            times.append(dic.get('times'))
            rule0_cnt.append(dic.get('rule0_cnt'))
            rule1_cnt.append(dic.get('rule1_cnt'))
            detail_cnt.append(dic.get('detail_cnt'))
            list_cnt.append(dic.get('list_cnt'))
            list_done_cnt.append(dic.get('list_done_cnt'))
        fp.close()
        return times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt


def convert_path_to_rule(url):
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    # print path
    pos = path.rfind('.')
    if pos > 0:
        suffix = path[pos:]
        path = path[:pos]
    else:
        suffix = ''
    # print suffix,path
    split_path = path.split('/')
    # print split_path
    new_path_list = []
    for p in split_path:
        regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', p)
        regex = re.sub(r'\d', '\d', regex)
        new_path_list.append(convert_regex_format(regex))
    # print new_path
    new_path = '/'.join(new_path_list) + suffix
    return urlparse.urlunparse(('', '', new_path, '', '', ''))


def convert_regex_format(rule):
    '''
    /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
    /news/\d{6}/[a-zA-Z]\d{8}_\d{6}.htm
    '''
    ret = ''
    digit = '\d'
    word = '[a-zA-Z]'
    cnt = 0
    pos = 0
    temp = ''
    while pos <= len(rule):
        if rule[pos:pos + len(digit)] == digit:
            if temp.find(digit) < 0:
                ret = ret + temp
                temp = ''
                cnt = 0
            cnt = cnt + 1
            temp = '%s{%d}' % (digit, cnt)
            pos = pos + len(digit)
        elif rule[pos:pos + len(word)] == word:
            if temp.find(word) < 0:
                ret = ret + temp
                temp = ''
                cnt = 0
            cnt = cnt + 1
            temp = '%s{%d}' % (word, cnt)
            pos = pos + len(word)
        elif pos == len(rule):
            ret = ret + temp
            break
        else:
            ret = ret + temp + rule[pos]
            temp = ''
            cnt = 0
            pos = pos + 1
    return ret


def modify_pyfile(py_file, start_urls, site_domain):
    try:
        lines = open(py_file, 'r').readlines()
        # print type(lines)
        i = 0
        for line in lines:
            s = line.strip()
            i += 1
            if s != '' and s[0] == '#':
                continue
            else:
                if i < 100 and re.search(r'self\.start_urls\s*?=', s):
                    lines[i - 1] = line[:line.find('=') + 1] + ' ' + start_urls + '\n'
                    print 'modify_pyfile()', lines[i - 1]

                if i < 100 and re.search(r'self\.site_domain\s*?=', s):
                    lines[i - 1] = line[:line.find('=') + 1] + ' ' + site_domain + '\n'
                    print 'modify_pyfile()', lines[i - 1]

        open(py_file, 'w').writelines(lines)

    except Exception, e:
        print 'modify_pyfile()', e


@app.route('/', methods=['GET', 'POST'])
def menu():
    # 清空主页、域名
    db = MySqlDrive()
    db.clean_current_main_setting()
    return render_template('menu.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', err=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', err=e), 500


@app.route('/convert', methods=["GET", "POST"])
def convert_to_regex():
    ret = {}
    convert_url = request.args.get('convert_url')
    ret['regex'] = convert_path_to_rule(convert_url)
    jsonStr = json.dumps(ret)
    print 'convert_to_regex()', convert_url, '->', jsonStr
    return jsonStr


@app.route('/show_process', methods=['GET', 'POST'])
def show_process():
    inputForm = InputForm()

    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain = mysql_db.get_current_main_setting()
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('show.html', inputForm=inputForm)

    # 从redis提取实时信息，转换成json文件
    redis_db = RedisDrive(start_url=start_url,
                          site_domain=site_domain,
                          redis_setting=redis_setting)
    redis_db.covert_redis_cnt_to_json()

    collage = CollageProcessInfo()
    times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt = collage.convert_file_to_list()
    times = range(len(times))  # 转换成序列[1,2,3...], high-chart不识别时间

    matched_rate = redis_db.get_matched_rate() * 100.0
    un_match_rate = 100.0 - matched_rate

    keywords, matched_cnt = redis_db.get_keywords_match()

    # 将json映射到html
    flash(u'每隔10秒刷新 ' + start_url + u' 的实时采集信息。')
    return render_template('show.html',
                           times=times,
                           rule1_cnt=rule1_cnt,
                           detail_cnt=detail_cnt,
                           list_cnt=list_cnt,
                           list_done_cnt=list_done_cnt,
                           matched_rate=matched_rate,
                           un_match_rate=un_match_rate,
                           keywords=keywords,
                           matched_cnt=matched_cnt)


@app.route('/show_result', methods=['GET', 'POST'])
def get_show_result():
    outputForm = OutputForm()

    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain = mysql_db.get_current_main_setting()
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('show-result.html', outputForm=outputForm)

    # 从redis提取实时信息，转换成json文件
    redis_db = RedisDrive(start_url=start_url,
                          site_domain=site_domain,
                          redis_setting=redis_setting)

    i = 0
    for list_url in redis_db.get_list_urls():
        list_url_data = MultiDict([('list_url', list_url), ('select', True)])
        list_url_form = ListUrlForm(list_url_data)
        outputForm.list_urls_list.entries[i] = list_url_form
        i += 1

    i = 0
    for detail_url in redis_db.get_detail_urls():
        detail_url_data = MultiDict([('detail_url', detail_url), ('select', True)])
        detail_url_form = DetailUrlForm(detail_url_data)
        outputForm.detail_urls_list.entries[i] = detail_url_form
        i += 1

    # result-list.txt
    fp = open(EXPORT_FOLDER + '/result-list.txt', 'w')
    for line in redis_db.conn.zrange(redis_db.list_urls_zset_key, 0, -1, withscores=False):
        fp.write(line + '\n')
    fp.close()

    # result-detail.txt
    fp = open(EXPORT_FOLDER + '/result-detail.txt', 'w')
    for line in redis_db.conn.zrange(redis_db.detail_urls_zset_key, 0, -1, withscores=False):
        fp.write(line + '\n')
    fp.close()

    return render_template('show-result.html', outputForm=outputForm)


@app.route('/setting_main_init', methods=['GET', 'POST'])
def setting_main_init():
    '''
    从MySql初始化Web页面和Redis
    '''
    inputForm = InputForm(request.form)

    mysql_db = MySqlDrive()
    start_url, site_domain = mysql_db.get_current_main_setting()
    if start_url is None or start_url.strip() == '' or \
                    site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、域名信息。')
        return render_template('setting.html', inputForm=inputForm)
    else:
        inputForm.start_url.data = start_url
        inputForm.site_domain.data = site_domain

    redis_db = RedisDrive(start_url=start_url,
                          site_domain=site_domain,
                          redis_setting=redis_setting)
    # 设置/还原 正则表达式-详情页
    i = 0
    for (black_domain, scope, white_or_black, weight, regex, etc) in mysql_db.get_regexs('detail'):
        regex_data = MultiDict([('select', True), ('regex', regex), ('weight', weight), ('score', int(0))])
        regexForm = RegexForm(regex_data)
        # inputForm.regex_list.append_entry(regexForm)
        inputForm.detail_regex_list.entries[i] = regexForm

        if redis_db.conn.zrank(redis_db.manual_detail_urls_rule_zset_key, regex) is None:
            redis_db.conn.zadd(redis_db.manual_detail_urls_rule_zset_key, 0, regex)

        i += 1

    # 设置/还原 正则表达式-列表页
    i = 0
    for (black_domain, scope, white_or_black, weight, regex, etc) in mysql_db.get_regexs('list'):
        regex_data = MultiDict([('select', True), ('regex', regex), ('weight', weight), ('score', int(0))])
        regexForm = RegexForm(regex_data)
        # inputForm.regex_list.append_entry(regexForm)
        inputForm.list_regex_list.entries[i] = regexForm

        if redis_db.conn.zrank(redis_db.manual_list_urls_rule_zset_key, regex) is None:
            redis_db.conn.zadd(redis_db.manual_list_urls_rule_zset_key, 0, regex)

        i += 1

    # 清除原有所有规则
    # db.conn.zremrangebyscore(db.detail_urls_rule1_zset_key, min=0, max=99999999)

    flash(u'初始化配置完成')
    return render_template('setting.html', inputForm=inputForm)


@app.route('/save_and_run', methods=['POST'])
def setting_main_save_and_run():
    inputForm = InputForm(request.form)
    # if inputForm.validate_on_submit():
    # if request.method == 'POST' and inputForm.validate():
    start_url = inputForm.start_url.data
    site_domain = inputForm.site_domain.data
    if start_url.strip() == '' or site_domain.strip() == '':
        flash(u'必须设置主页、域名信息！')
        return render_template('setting.html', inputForm=inputForm)

    # 正则保存对象-详情页
    detail_regex_list = inputForm.detail_regex_list.data
    detail_regex_save_list = []
    detail_regex_cnt = 0
    for r in detail_regex_list:
        select = r['select']
        regex = r['regex']
        weight = r['weight']
        score = r['score']
        if select and regex != '':
            detail_regex_cnt += 1
            detail_regex_save_list.append((regex, weight))

    # 正则保存对象-列表页
    list_regex_list = inputForm.list_regex_list.data
    list_regex_save_list = []
    list_regex_cnt = 0
    for r in list_regex_list:
        select = r['select']
        regex = r['regex']
        weight = r['weight']
        score = r['score']
        if select and regex != '':
            list_regex_cnt += 1
            list_regex_save_list.append((regex, weight))

    if len(list_regex_save_list) + len(detail_regex_save_list) == 0:
        flash(u"请填写并勾选要执行的 列表/详情页正则表达式。")
        return render_template('setting.html', inputForm=inputForm)

    # 保存到json文件
    export_file = {'start_url': start_url,
                   'site_domain': site_domain,
                   'detail_regex_save_list': detail_regex_save_list,
                   'list_regex_save_list': list_regex_save_list
                   }
    seeting_json = json.dumps(export_file)
    open(EXPORT_FOLDER + 'export.json', 'w').write(seeting_json)

    # 保存手工配置规则到Redis
    redis_db = RedisDrive(start_url=start_url,
                          site_domain=site_domain,
                          redis_setting=redis_setting)
    for regex in redis_db.conn.zrange(redis_db.manual_list_urls_rule_zset_key, start=0, end=-1):
        redis_db.conn.zrem(redis_db.manual_list_urls_rule_zset_key, regex)
    for (regex, weight) in list_regex_save_list:
        redis_db.conn.zadd(redis_db.manual_list_urls_rule_zset_key, 0, regex)

    for regex in redis_db.conn.zrange(redis_db.manual_detail_urls_rule_zset_key, start=0, end=-1):
        redis_db.conn.zrem(redis_db.manual_detail_urls_rule_zset_key, regex)
    for (regex, weight) in detail_regex_save_list:
        redis_db.conn.zadd(redis_db.manual_detail_urls_rule_zset_key, 0, regex)

    # 保存所有手工配置信息到MySql
    mysql_db = MySqlDrive()
    mysql_db.set_current_main_setting(start_url, site_domain, seeting_json)
    cnt = mysql_db.save_all_setting(start_url, site_domain, seeting_json, detail_regex_save_list,
                                    list_regex_save_list)
    if cnt == 1:
        flash(u"MySQL保存完毕，执行中...")
    else:
        flash(u"MySQL保存失败，执行中...")

    # 执行抓取程序 RUN_PY_FILE
    # 修改配置文件的执行入口信息
    modify_pyfile(py_file=RUN_PY_FILE, start_urls="\'" + start_url + "\'", site_domain="\'" + site_domain + "\'")
    # DOS "start" command
    if os.name == 'nt':
        os.startfile(RUN_PY_FILE)
    else:
        print os.system('./run_spider.sh')
        # os.popen("python " + RUN_PY_FILE)
        # print p.read()

    return render_template('setting.html', inputForm=inputForm)


@app.route('/export/<path:filename>')
def download_file(filename):
    print 'download_file()',filename
    return send_from_directory(app.config['EXPORT_FOLDER'], filename, as_attachment=True)


@app.route('/export_upload', methods=['GET', 'POST'])
def export_upload():
    if request.method == 'GET':
        return render_template('export.html')

    elif request.method == 'POST':
        f = request.files['file']
        # 获取一个安全的文件名，仅支持ascii字符。
        f_name = secure_filename(f.filename)
        f.save(os.path.join(EXPORT_FOLDER, f_name))
        flash(u"上传成功.")
        return render_template('export.html')


@app.route('/export_setting_json', methods=['GET', 'POST'])
def export_setting():
    mysql_db = MySqlDrive()
    start_url, site_domain = mysql_db.get_current_main_setting()
    setting_json = ''
    flash(u"MySQL导出结果。")
    return render_template('export.html', setting_json=setting_json)


@app.route('/export_init')
def export_import():
    flash(u"请选择导入/导出操作。")
    return redirect(url_for('export_upload'), 302)


if __name__ == '__main__':
    app.run(debug=True)

    # -------------------unit test-----------------------------------
    # mysql = MySqlDrive()
    # print mysql.save_to_mysql('http://bbs.tianya.com','bbs.tianya.con','aaaaaaaaaaaaaaa')
    # print mysql.get_current_main_setting()
