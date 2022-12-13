# -*- coding: utf-8 -*-
import requests
import json
import os

class WeChat():
    def __init__(self, appid="", app_secret="") -> None:
        self.appid = appid
        self.secret = app_secret   
        self.token = None     
    
    # 获得token
    # self.token = token
    def get_access_token(self):
        '''
        获取微信的access_token： 获取调用接口凭证
        return: token
        '''
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret,
        }
        url = f"https://api.weixin.qq.com/cgi-bin/token"
        response = requests.get(url, params=params)
        res = response.json()
        print("get_access_token", res)
        if "access_token" in res:
            token = res["access_token"]
            self.token = token
            return token
    
    # 获得草稿列表
    def get_draft_list(self, offset=0, count_=20, no_content=1):
        params = {
            "access_token": self.token,
        }
        data = {
            "offset": offset,
            "count": count_,
            "no_content": no_content,
        }
        url = "https://api.weixin.qq.com/cgi-bin/draft/batchget"
        response = requests.post(url=url, params=params, data=json.dumps(data))
        res = response.json()
        print("get_draft_list", res)
    
    # 获得草稿数量
    def count_draft(self):
        params = {
            "access_token": self.token,
        }
        url = "https://api.weixin.qq.com/cgi-bin/draft/batchget"
        response = requests.get(url=url, params=params)
        res = response.json()
        print("count_draft", res)
        
    # 新建草稿 
    def add_draft(self, articles=None):
        params = {
            "access_token": self.token,
        }
        data = {
            "articles": articles,
        }
        url = "https://api.weixin.qq.com/cgi-bin/draft/add"
        response = requests.post(url=url, params=params, data=json.dumps(data, ensure_ascii=False).encode("utf-8").decode("latin1"))
        res = response.json()
        print("add_draft", res)
        return res.get("media_id")
        
    # 获取草稿
    def get_draft(self, media_id=None):
        params = {
            "access_token": self.token,
        }
        data = {
            "media_id": media_id,
        }
        url = "https://api.weixin.qq.com/cgi-bin/draft/get"
        response = requests.post(url=url, params=params, data=json.dumps(data))
        res = response.json()
        print("get_draft", res)
        
    # 删除草稿
    def delete_draft(self, media_id=None):
        params = {
            "access_token": self.token,
        }
        data = {
            "media_id": media_id,
        }
        url = "https://api.weixin.qq.com/cgi-bin/draft/delete"
        response = requests.post(url=url, params=params, data=json.dumps(data))
        res = response.json()
        print("delete_draft", res)
    
    # 修改草稿
    def update_draft(self, media_id=None, index=None, articles=None):
        params = {
            "access_token": self.token,
        }
        data = {
            "media_id": media_id,
            "index": index,
            "articles": articles,
        }
        url = "https://api.weixin.qq.com/cgi-bin/draft/update"
        response = requests.post(url=url, params=params, data=json.dumps(data))
        res = response.json()
        print("update_draft", res)
        
    # 获取素材列表
    def get_material_list(self, type_="image", offset=0, count_=20):
        params = {
            "access_token": self.token,
        }
        data = {
            "type": type_,
            "offset": offset,
            "count": count_,
        }
        url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material"
        response = requests.post(url=url, params=params, data=json.dumps(data))
        res = response.json()
        print("get_material_list", res)
        if "errcode" not in res:
            return res["item"]
        return 0
    
    # 获取素材数量
    def count_material(self):
        params = {
            "access_token": self.token,
        }
        url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material"
        response = requests.get(url=url, params=params)
        res = response.json()
        print("count_material", res)
        if "errcode" not in res:
            return res
        return 0

    # 上传图文消息内的图片获取URL
    def upload_image(self, file_name=None, server_name=None):
        params = {
            "access_token": self.token,
        }
        file = {
            "file1": (server_name, open(file_name, "rb"), "image/png", {"Expire": "0"}),
        }
        url = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
        response = requests.post(url=url, params=params, files=file)
        res = response.json()
        print("upload_image", res)
        return res.get("url")
        
        
    # 新增其他类型临时素材。
    def upload_material(self, type_="image", file_name=None, title=None, introduction=None):
        params = {
            "access_token": self.token,
            "type": type_,
        }
        file = {
            "media": open(file_name, "rb"),
        }
        url = "https://api.weixin.qq.com/cgi-bin/media/upload"
        response = requests.post(url=url, params=params, files=file)
        res = response.json()
        print("upload_material", res)
        return res.get("media_id")
    
    # 发布草稿
    def submit(self, media_id):
        params = {
            "access_token": self.token,
        }
        data = {
            "media_id": media_id,
        }
        url = "https://api.weixin.qq.com/cgi-bin/freepublish/submit"
        response = requests.post(url=url, params=params, data=json.dumps(data))
        res = response.json()
        print("submit", res)
        return res.get("publish_id")
        

# weixin = WeChat()
# weixin.get_access_token()
# print(weixin.get_material_list())
# print(weixin.add_material(file_name="temp.png", server_name="temp.png"))
