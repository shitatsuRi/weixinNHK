# -*- coding: utf-8 -*-
from nhk import NHKScrapy
from wechat import WeChat
from datetime import date, datetime, timedelta

import os
import os.path
import re


def main(date_=None):
    nhk = NHKScrapy()
    TODAY = date.today()
    TODAY_STR = datetime.strftime(TODAY, '%Y-%m-%d')
    YESTERDAY = (TODAY + timedelta(days=-1)) if not date_ else date_
    YESTERDAY_STR = datetime.strftime(YESTERDAY, '%Y-%m-%d')

    nhk_res = nhk.run(YESTERDAY_STR)
    
    wechat = WeChat()
    wechat.get_access_token()
    articles = []
    for key, value in nhk_res.items():
        media_id = ""
        media_name = f"nhk/{key}/{key}.jpg"
        media_url = ""
        # 如果有新闻图片就上传图片
        if os.path.exists(media_name):
            media_id = wechat.upload_material(type_="image", file_name=media_name)
            media_url = wechat.upload_image(file_name=media_name, server_name=f"{key}.jpg")
        # # 如果上传不成功，或者没有图片，就用通用封面
        # if not media_id:
        #     media_id = "Jms241ibC-PJB2pIMrCi3z3hW2IiSzYJYIbCOte0_3VoTzX6G4UHS3wZ79Rblo3H"
        title = re.sub(r"\(.*?\)|\[|\]", "", value["title"])
        content = (
            (f"<h1>{value['title']}</h1>"+f"<img src='{media_url}'>"+value["news_body_text"])
            .replace("[", "<ruby>")
            .replace("]", "</ruby>")
            .replace("(", "<rt>")
            .replace(")", "</rt>"))
        article = {
            "title":title[:10]+"...",
            "author":"kitab",
            "content":content,
            "thumb_media_id":"Jms241ibC-PJB2pIMrCi31FOGSjmirmVAGZQtEgfepKDozKzv3CimFGmRpstVxdn",
        }
        articles.append(article)
    # print(articles)
    draft_id = wechat.add_draft(articles=articles)
    # wechat.submit(media_id=draft_id)
    
    
if __name__ == "__main__":
    main()