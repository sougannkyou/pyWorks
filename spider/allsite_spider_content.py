#!/usr/bin/python
# coding=utf-8

import os
import datetime
import htmlparser
import redis
import spider
import setting
import ConfigParser
from bs4 import BeautifulSoup, Comment
import json
import allsite_clean_url

####################################################################
MY_OS = os.getenv('SPIDER_OS')
if MY_OS is None:
    print '[ERROR] must be set a MY_OS.'
    exit(-1)
else:
    print '[info]--- The OS is: %s ----' % MY_OS
    if MY_OS == 'linux':
        INIT_CONFIG = '/work/spider/allsite_spider.ini'
    elif MY_OS == 'mac':
        INIT_CONFIG = '/Users/song/workspace/pyWorks/spider/allsite_spider.ini'
    else:  # windows
        INIT_CONFIG = './allsite_spider.ini'
####################################################################
config = ConfigParser.ConfigParser()
if len(config.read(INIT_CONFIG)) == 0:
    print '[ERROR]cannot read the config file.', INIT_CONFIG
    exit(-1)
else:
    print '[INFO] read the config file.', INIT_CONFIG

EXPORT_FOLDER = config.get(MY_OS, 'export_folder')
# redis
REDIS_SERVER = config.get('redis', 'redis_server')
DEDUP_SETTING = config.get('redis', 'dedup_server')

# spider-modify-start
START_URLS = '''http://bbs.tianya.cn'''
SITE_DOMAIN = '''bbs.tianya.cn'''
BLACK_DOMAIN_STR = ''''''
TITLE_EXP = ''''''
CONTENT_EXP = ''''''
AUTHOR_EXP = ''''''
CTIME_EXP = ''''''


# spider-modify-end

# TITLE_EXP = '''.//*[@id='post_head']/h1/span[1]/span'''
# CONTENT_EXP = '''.//*[@id='bd']/div[4]/div[1]/div/div[2]/div[1]'''
# AUTHOR_EXP = '''.//*[@id='post_head']/div[2]/div[2]/span[1]/a'''
# CTIME_EXP = '''.//*[@id='post_head']/div[2]/div[2]/span[2]'''

# START_URLS = config.get('spider', 'start_urls')
# SITE_DOMAIN = config.get('spider', 'site_domain')
# BLACK_DOMAIN_LIST = config.get('spider', 'black_domain_list')
# DETAIL_RULE_LIST = config.get('spider', 'detail_rule_list')
# LIST_RULE_LIST = config.get('spider', 'list_rule_list')
#############################################################################

class MySpider(spider.Spider):
    def __init__(self,
                 proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        spider.Spider.__init__(
            self, proxy_enable, proxy_max_num, timeout=timeout, cmd_args=cmd_args)
        # 网站名称
        self.siteName = "all"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        self.start_urls = START_URLS
        self.site_domain = SITE_DOMAIN
        self.black_domain_list = BLACK_DOMAIN_STR
        # xpath或regex,采集 标题,做成时间,内容,作者。
        self.title_sel = 'xpath'
        self.title_exp = TITLE_EXP
        self.ctime_sel = 'xpath'
        self.ctime_exp = CTIME_EXP
        self.content_sel = 'xpath'
        self.content_exp = CONTENT_EXP
        self.author_sel = 'xpath'
        self.author_exp = AUTHOR_EXP

        self.encoding = 'utf-8'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.detail_urls_set_key = 'detail_urls_set_%s' % self.site_domain  # 输入详情页URL
        self.todo_urls_limits = 100
        self.dedup_key = 'dedup'

    def setting_init(self, setting_dict):
        self.start_urls = setting_dict['start_url']
        self.site_domain = setting_dict['site_domain']
        self.black_domain_list = setting_dict['black_domain_str']
        # xpath或regex,采集 标题,做成时间,内容,作者。
        self.title_sel = setting_dict['title_sel']
        self.title_exp = setting_dict['title_exp']
        self.ctime_sel = setting_dict['ctime_sel']
        self.ctime_exp = setting_dict['ctime_exp']
        self.content_sel = setting_dict['content_sel']
        self.content_exp = setting_dict['content_exp']
        self.author_sel = setting_dict['author_sel']
        self.author_exp = setting_dict['author_exp']

    def get_start_urls(self, data=None):
        return [self.start_urls]

    def parse(self, response):
        urls = []
        for i in range(self.todo_urls_limits):
            url = self.conn.spop(self.detail_urls_set_key)
            if url is not None or url != '':
                urls.append(url)

        return urls, None, None

    def parse_detail_page(self, response=None, url=None):
        try:
            response.encoding = self.encoding
            unicode_html_body = response.text
            data = htmlparser.Parser(unicode_html_body)
        except Exception, e:
            print "[ERROR]parse_detail_page(): %s" % e
            return None
        if url is None:
            url = response.request.url

        result = []
        title = data.xpath(self.title_exp).text().strip()
        print 'title:', type(title), title
        source = self.siteName
        ctime = data.xpath(self.ctime_exp).replace(u'年', '-').replace(u'月', '-').replace(u'日', ''). \
            regex('(\d+-\d+-\d+)').datetime()
        content = data.xpath(self.content_exp).text().strip()
        utc_now = datetime.datetime.utcnow()
        author = data.xpath(self.author_exp).text().strip()
        post = {'url': url,
                # 'title': unicode(title,encoding='utf-8'),
                'title': title,
                # 'content': unicode(content,encoding='utf-8'),
                'content': content,
                'ctime': '',
                'utc_now': '',
                # 'author': unicode(author,encoding='utf-8'),
                'author': author,
                }
        print '[INFO]parse_detail_page()', post
        result.append(post)
        return result


def get_all(setting_json):
    detail_job_list = []  # equal to run.py detail_job_queue

    # ---equal to run.py get_detail_page_urls(spider, urls, func, detail_jo
    def __detail_page_urls(urls, func):
        next_page_url = None
        if func is not None:
            if urls:
                for url in urls:
                    try:
                        response = mySpider.download(url)
                        list_urls, callback, next_page_url = func(response)  # parse()
                        for url in list_urls:
                            detail_job_list.append(url)
                    except Exception, e:
                        print '[ERROR] main() Exception: %s' % e
                        list_urls, callback, next_page_url = [], None, None

                    __detail_page_urls(list_urls, callback)

                    if next_page_url is not None:
                        print 'next_page_url'
                        __detail_page_urls([next_page_url], func)

    # --equal to run.py list_page_thread() -------------------------
    mySpider = MySpider()
    mySpider.proxy_enable = False
    mySpider.init_dedup()
    mySpider.init_downloader()
    start_urls = mySpider.get_start_urls()  # get_start_urls()
    print '[test]start_urls:', start_urls
    __detail_page_urls(start_urls, mySpider.parse)  # parse()

    # --equal to run.py detail_page_thread() -------------------------
    for url in detail_job_list:
        resp = mySpider.download(url)
        ret = mySpider.parse_detail_page(resp, url)  # parse_detail_page()
        for item in ret:
            print '----------------------------------------------------'
            for k, v in item.iteritems():
                print k, v


def get_one(url, setting_dict):
    print '[INFO]get_one() start.', url, setting_dict
    mySpider = MySpider()
    mySpider.setting_init(setting_dict)
    mySpider.proxy_enable = False
    mySpider.init_dedup()
    mySpider.init_downloader()
    response = mySpider.download(url)
    one = mySpider.parse_detail_page(response, url)
    print '[INFO]get_one() end.', one
    if one:
        return one[0]
        # return {'url': url,
        #         'title': 'error',
        #         'content': 'error',
        #         'ctime': 'error',
        #         'author': 'error',
        #         }
    else:
        return {'url': url,
                'title': 'error',
                'content': 'error',
                'ctime': 'error',
                'author': 'error',
                }


if __name__ == '__main__':
    url = 'http://bbs.tianya.cn/post-41-1236689-1.shtml'
    setting_dict = {
        "start_url": "http://bbs.tianya.cn",
        "site_domain": "bbs.tianya.cn",
        "black_domain_str": "",
        "title_sel": "xpath",
        "title_exp": ".//*[@id='post_head']/h1/span[1]/span",
        "ctime_sel": "xpath",
        "ctime_exp": ".//*[@id='post_head']/div[2]/div[2]/span[2]",
        "content_sel": "xpath",
        "content_exp": ".//*[@id='bd']/div[4]/div[1]/div/div[2]/div[1]",
        "author_sel": "xpath",
        "author_exp": ".//*[@id='post_head']/div[2]/div[2]/span[1]/a"
    }
    ret = get_one(url, setting_dict)
    print ret
    for k, v in ret.iteritems():
        print k, v
