from flask import Flask, request,redirect
from os import path,execl
from sys import executable,argv
from function import getNewImage, keepToken, reqToken
from threading import Thread
from time import sleep
app = Flask(__name__)
dir_path = path.dirname(path.realpath(__file__))

# @app.after_request
# def after_request_func(response):
#     print("after_request is running!")
#     if (path.exists(dir_path + "/token.json")):
#         sleep(10)
#         execl(executable, path.abspath(__file__), *argv)
#     return response

class Compute(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        sleep(2)
        execl(executable, path.abspath(__file__), *argv)

@app.route('/')
def firstPage():
    if ("oauth_token" in request.args.keys() and "oauth_verifier" in request.args.keys()):
        keepToken()
        Compute().start()
        return "Complete! Restart<script>window.close();</script>"
    return "Hello World"

@app.route('/login')
def loginPage():
    oauth_token = reqToken()
    return redirect("https://api.twitter.com/oauth/authenticate?oauth_token=" + oauth_token,302)

if __name__ == '__main__':
    if (not path.exists(dir_path + "/token.json")):
        from webbrowser import open
        open("http://localhost:3000/login")
        app.run(port=3000)
    else:
        while True:
            getNewImage()