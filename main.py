from flask import Flask, render_template
import sqlite3
import json   
              
dbpath = 'test.db' #テーブルを保存するファイル
app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello():
    return render_template("app.html")


if __name__ == "__main__":
    # 最後に消す!!!
    app.debug = True
    app.run(host="localhost") 

