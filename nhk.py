# -*- coding: utf-8 -*-
import requests
import os
import os.path
import time
import re
from lxml import etree
from datetime import datetime, timedelta
import json
import logging
from logging import handlers

# 没有找到json文件中对应的日期
class WrongDateError(Exception):
    pass

# 日志输出类
class Logger(object):
    def __init__(self,filename,level=logging.INFO,when='D',backCount=3,fmt='%(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(level)#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        th.setFormatter(format_str)#设置文件里写入的格式
        if not self.logger.handlers: # 新增handles时判断是否为空
            self.logger.addHandler(sh) #把对象加到logger里
            self.logger.addHandler(th)
 
class NHKScrapy():
    def __init__(self) -> None:
        # 设置时间常数
        self.TODAY = datetime.today()
        self.TODAY_STR = datetime.strftime(self.TODAY, '%Y-%m-%d')
        self.YESTERDAY = self.TODAY + timedelta(days=-1)
        self.YESTERDAY_STR = datetime.strftime(self.YESTERDAY, '%Y-%m-%d')
        # 设置请求头
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Referer": "https://www.nhk.or.jp/",
            "Connection": "keep-alive",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        }
        self.TEXT_HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Referer": "https://www3.nhk.or.jp/",
            "Connection": "keep-alive",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        }
        self.PARSER = etree.HTMLParser(encoding='utf-8')
        self.LOG = None

    # 有效化文件名
    def validateTitle(self, title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title if new_title else str(int(round(time.time()*1000)))

    # 创建文件夹
    def makeDir(self, io):
        isexist = os.path.exists(io)
        if not isexist:
            os.makedirs(io)

    # 将带html标签文本转换为括号
    def StrTree(self, str1):
        return re.sub(r"<.*?>", "", 
                    str1.replace("<ruby>", "[")
                    .replace("</ruby>", "]")
                    .replace("<rt>", "(")
                    .replace("</rt>", ")")
                    .replace("\u3000", "").strip())

    # 获取NHK文章列表
    def getNewsJson(self, date=None):
        date = self.YESTERDAY_STR if not date else date
        file_path = f'nhk/news-list/{date}-news-list.json'
        if os.path.exists(file_path):
            self.LOG.logger.info("already exist list")
            with open(file_path, 'r', encoding='utf-8') as fp:
                result = json.load(fp)
                # 找到当前日期的
                if date not in result[0].keys():
                    raise WrongDateError(f'news in {date} not found')
                return result[0][date] 
            
        NEWS_URL = "https://www3.nhk.or.jp/news/easy/news-list.json"
        with requests.Session() as session:
            response = session.get(url=NEWS_URL, headers=self.TEXT_HEADERS)
            if response.status_code == requests.codes.ok:
                # utf-8-sig处理方法：去掉content前三个字符
                content = response.content[3:].decode('utf8')
                # 把所有的文章列表写入文件
                with open(file_path, "w", encoding="utf-8") as fp:
                    fp.write(content)
                result = json.loads(content)
                self.LOG.logger.info("save news list")
                # 找到当前日期的
                if date not in result[0].keys():
                    raise WrongDateError(f'news in {date} not found')
                return result[0][date]

    # 获取文章文本内容
    def getArticleText(self, id, date=None):
        date = self.YESTERDAY_STR if not date else date
        file_path = f"nhk/{date}/{id}.txt"
        if os.path.exists(file_path):
            self.LOG.logger.info("already exist news")
            with open(file_path, "r", encoding="utf-8") as fp:
                return re.findall(r'</h1>(.*?)<p></p>', fp.read())[0]
            
        TEXT_URL = f"https://www3.nhk.or.jp/news/easy/{id}/{id}.html"
        with requests.Session() as session:
            response = session.get(url=TEXT_URL, headers=self.TEXT_HEADERS)
            time.sleep(1)
            if response.status_code == requests.codes.ok:
                response.encoding = "utf-8"
                tree = etree.HTML(response.text, parser=self.PARSER)
                title = tree.xpath("//title//text()")[0]
                article_title = tree.xpath("//h1[@class='article-main__title']")[0]
                article_title_text = self.StrTree(
                    etree.tostring(article_title, encoding="utf-8").decode("utf-8")).strip()
                # 把多段合并成一个字符串写入
                article_body_text = ''.join(["<p>"+self.StrTree(etree.tostring(i, encoding="utf-8").decode("utf-8"))+"</p>"
                    for i in tree.xpath("//div[@class='article-main__body article-body']/p")])
                title = self.validateTitle(f"{id}_{title}")
                with open(file_path, "w", encoding="utf-8") as fp:
                    fp.writelines("<h1>")
                    fp.writelines(self.StrTree(article_title_text))
                    fp.writelines("</h1>")
                    fp.write(article_body_text)
                self.LOG.logger.info(f"save\t{date} news\t{id}")
                return article_body_text

    # 获取新闻封面图片
    def getNewsImage(self, id, image_url):
        file_path = f"nhk/{id}/{id}.jpg"
        if os.path.exists(file_path):
            self.LOG.logger.info(f"already exist image\t{id}")
            return None
        
        with requests.Session() as session:
            response = session.get(url=image_url, headers=self.TEXT_HEADERS)
            time.sleep(1)
            if response.status_code == requests.codes.ok:
                with open(file_path, "wb") as fp:
                    fp.write(response.content)
                self.LOG.logger.info(f"save image\t{id}")

    # 获取NHK信息主程序
    def run(self, date=None):
        date = self.YESTERDAY_STR if not date else date
        try:
            # 新建一个文件夹放文章列表文件
            self.makeDir('nhk')
            self.LOG = Logger('nhk/nhk-news.log')
            self.makeDir('nhk/news-list')
            info = self.getNewsJson(date=date)
            self.makeDir(f'nhk/{date}')
            ids_ = {}
            for news in info:
                id = news['news_id']
                ids_[id] = {
                    'title': self.StrTree(news['title_with_ruby']),
                    'news_body_text': self.getArticleText(id=id, date=date)}
                # news['news_body_text'] = self.getArticleText(id=id, date=date)
                self.makeDir(f'nhk/{id}')
                if news['news_web_image_uri']:
                    self.getNewsImage(id=id, image_url=news['news_web_image_uri'])
            with open(f'nhk/{date}/{date}.json', 'w', encoding='utf-8') as fp:
                json.dump(ids_, fp, ensure_ascii=False, )
            self.LOG.logger.info(f"save json {date}")
            return ids_
        except WrongDateError:
            self.LOG.logger.info(f"news in {date} not found")
            return 0

if __name__ == "__main__":
    nhk = NHKScrapy()
    TODAY = datetime.strptime('2022-08-18', '%Y-%m-%d')
    TODAY_STR = datetime.strftime(TODAY, '%Y-%m-%d')
    YESTERDAY = TODAY + timedelta(days=-1)
    YESTERDAY_STR = datetime.strftime(YESTERDAY, '%Y-%m-%d')
    # schedule.every().days.at("18:00").do(nhk.run)
    # while True:
    #     schedule.run_pending()
    print(nhk.run(YESTERDAY_STR))
