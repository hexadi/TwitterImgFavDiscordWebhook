from requests import post,get
from requests_oauthlib import OAuth1
from flask import request
from os import path
from json import dumps, loads
from time import sleep
dir_path = path.dirname(path.realpath(__file__))

def read_env(file=".env"):
    read_file = open(dir_path + "/" + file, "r")
    split_file = [r.strip().split("=",maxsplit=1) for r in read_file.readlines()]
    key,value = zip(*split_file)
    return dict(zip(key,value))

def read_params(text):
    textList = [item.split("=",maxsplit=1) for item in text.split("&")]
    key,value = zip(*textList)
    return dict(zip(key,value))
    

config = read_env()

def send_Webhook(url,data):
    return post(url,headers={"content-type":"application/json"},data=data)

def writeFile(fileName,data):
    file = open(fileName, "w")
    file.write(data)
    file.close()

def keepToken():
    r = post(url="https://api.twitter.com/oauth/access_token?oauth_token={}&oauth_verifier={}".format(request.args.get("oauth_token"),request.args.get("oauth_verifier")))
    params = read_params(r.text)
    resource_owner_key = params["oauth_token"]
    resource_owner_secret = params["oauth_token_secret"]
    screen_name = params["screen_name"]
    writeFile(dir_path + "/token.json",dumps({"oauth_token": resource_owner_key, "oauth_secret": resource_owner_secret, "screen_name": screen_name}))

def reqToken():
    client_key = config['client_key']
    client_secret = config['client_secret']
    oauth = OAuth1(client_key, client_secret=client_secret)
    r = post(url="https://api.twitter.com/oauth/request_token", auth=oauth)
    return read_params(r.text)["oauth_token"]

def getNewImage():
    token = open(dir_path + "/token.json", "r")
    token_ = loads(token.read())
    token.close()
    oauth = OAuth1(client_key=config['client_key'], client_secret=config['client_secret'], resource_owner_key=token_["oauth_token"], resource_owner_secret=token_["oauth_secret"])
    r = get("https://api.twitter.com/1.1/favorites/list.json?screen_name=" + token_["screen_name"] + "&include_entities=true&tweet_mode=extended",auth=oauth)
    response = r.json()
    if ("latest" not in token_):
        token_["latest"] = response[1]["id"]
    for post in response:
        if ("media" in post["entities"] and post["id"] > token_["latest"]):
            for media in post["entities"]["media"]:
                send_Webhook(config["discord_webhook"],dumps({"content":media["media_url_https"]}))
    token_["latest"] = response[0]["id"]
    writeFile(dir_path + "/token.json",dumps(token_))
    sleep(float(config['timeout']))