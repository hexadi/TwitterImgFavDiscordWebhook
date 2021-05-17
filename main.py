from flask import Flask, request, redirect
import requests,os,json,sys
from requests_oauthlib import OAuth1
from dotenv import dotenv_values
from time import sleep
config = dotenv_values(".env")
app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
@app.route('/')
def hello_world():
    if ("oauth_token" in request.args.keys() and "oauth_verifier" in request.args.keys()):
        r = requests.post(url="https://api.twitter.com/oauth/access_token?oauth_token={}&oauth_verifier={}".format(request.args.get("oauth_token"),request.args.get("oauth_verifier")))
        resource_owner_key = r.text.split("oauth_token=")[1].split("&oauth_token_secret")[0]
        resource_owner_secret = r.text.split("&oauth_token_secret=")[1].split("&user_id")[0]
        screen_name = r.text.split("&screen_name=")[1]
        token_file = open(dir_path + "/token.json", "w")
        token_file.write(json.dumps({"oauth_token": resource_owner_key, "oauth_secret": resource_owner_secret, "screen_name": screen_name}))
        token_file.close()
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    else:
        return "Hello World"

@app.route('/login')
def loginPage():
    client_key = config['client_key']
    client_secret = config['client_secret']
    oauth = OAuth1(client_key, client_secret=client_secret)
    r = requests.post(url="https://api.twitter.com/oauth/request_token", auth=oauth)
    oauth_token = r.text.split("=")[1].split("&")[0]
    return redirect("https://api.twitter.com/oauth/authenticate?oauth_token=" + oauth_token,302)

if __name__ == '__main__':
    if (not os.path.exists(dir_path + "/token.json")):
        import webbrowser
        webbrowser.open("http://localhost:3000/login")
        app.run(port=3000)
    else:
        while True:
            token = open(dir_path + "/token.json", "r")
            token_ = json.loads(token.read())
            token.close()
            oauth = OAuth1(client_key=config['client_key'], client_secret=config['client_secret'], resource_owner_key=token_["oauth_token"], resource_owner_secret=token_["oauth_secret"])
            r = requests.get("https://api.twitter.com/1.1/favorites/list.json?screen_name=" + token_["screen_name"] + "&include_entities=true&tweet_mode=extended",auth=oauth)
            response = r.json()
            if ("latest" not in token_):
                token_["latest"] = response[1]["id"]
            for post in response:
                if ("media" in post["entities"] and post["id"] > token_["latest"]):
                    for media in post["entities"]["media"]:
                        rp = requests.post(config["discord_webhook"],headers={"content-type":"application/json"},data=json.dumps({"content":media["media_url_https"]}))
            token_["latest"] = response[0]["id"]
            token = open(dir_path + "/token.json", "w")
            token.write(json.dumps(token_))
            token.close()
            sleep(float(config['timeout']))