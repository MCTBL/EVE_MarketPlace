import requests as req
import json
import datetime
from dateutil import tz
import os

token_url = "https://login.evepc.163.com/v2/oauth/token"
token = os.environ.get("REFRESH_TOKEN").strip()
appID = os.environ.get("APP_ID").strip()
appSecret = os.environ.get("APP_Secret").strip()
openID = os.environ.get("OPEN_ID").strip()
templateID = os.environ.get("TEMPLATE_ID").strip()
client_id = os.environ.get("CLIENT_ID").strip()

refresh_token = {
    "grant_type": "refresh_token",
    "refresh_token": token,
    "client_id": client_id
}
access_token = ""
wechatAccess = ""
userName = ""
userID = -1
baseUrl = "https://ali-esi.evepc.163.com"
datasource = "serenity"


def checkAnUpdateToken():
    global access_token
    global refresh_token
    head = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Connection": "close"
    }
    response = req.post(token_url, data=refresh_token, headers=head)
    if response.status_code == 200:
        access_token = json.loads(response.content)["access_token"]


def getCharacterIDAndName():
    global access_token
    global userName
    global userID
    checkAnUpdateToken()
    response = req.get(
        "https://ali-esi.evepc.163.com/verify?token={}".format(access_token))
    if response.status_code == 200:
        respon = json.loads(response.content)
        userName = respon["CharacterName"]
        userID = respon["CharacterID"]


def getWeChatAccess():
    global wechatAccess
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID, appSecret)
    wechatAccess = json.loads(req.get(url).content)["access_token"]


def sendInfo(nowTime, userName, balance):
    getWeChatAccess()
    body = {
        "touser": openID,
        "template_id": templateID,
        "url": "https://weixin.qq.com",
        "data": {
            "nowTime": {
                "value": nowTime
            },
            "userName": {
                "value": userName
            },
            "balance": {
                "value": balance
            }
        }
    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(
        wechatAccess)
    req.post(url, json.dumps(body)).text


if __name__ == "__main__":
    getCharacterIDAndName()
    url = baseUrl + "/legacy/characters/{}/wallet/?datasource={}&token={}".format(
        str(userID), datasource, access_token)
    balance = str('{:,}'.format(
        round(float(json.loads(req.get(url).content)), 2)))
    nowtime = datetime.datetime.now(tz=tz.gettz(
        "Asia/China")).strftime("%Y-%m-%d %H:%M:%S")
    sendInfo(nowtime, userName, balance)
