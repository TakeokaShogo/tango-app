from flask import *
from flask_sqlalchemy import SQLAlchemy

# 必ず消す!!
# from flask_cors import CORS

import csv
import re
import os
              
app = Flask(__name__)

# 必ず消す!!
# CORS(app)

# RuntimeError: Working outside of application context. 対策
with app.app_context():
    # アップデートの追跡機能の無効化
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # db_type = "sqlite"
    # db_file_path = 'test.db'
    # db_uri = db_type + ":///" + db_file_path

    # fly.ioの環境変数を参照する
    db_uri = os.environ.get('DATABASE_URL')

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db = SQLAlchemy(app)

    class WordList(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        # "none", "red", "yellow"
        category = db.Column(db.String(10), index=False, unique=False)
        # 検索はしないため、index(索引用のデータ)はFalse
        en_word = db.Column(db.String(15), index=False, unique=True)
        # "じっと見る"という意味の単語が二つあったため、uniqueはFalse
        ja_meaning = db.Column(db.String(100), index=False, unique=False)

    db.create_all()

# 2.2.xで非推奨。2.3では削除される予定
@app.before_first_request
def insert_word_list():
    # データベースが空でなければreturn
    if WordList.query.all():
        return

    with open("words-list-formatted.csv", 'r', encoding="utf8") as f:
        reader = csv.reader(f)
        for row in reader:
            en_word = row[1]
            ja_meaning = row[2]
            word_list = WordList(category="none", en_word=en_word, ja_meaning=ja_meaning)
            db.session.add(word_list)
            db.session.commit()

@app.route('/', methods=["GET"])
def render_app():
    return render_template("index.html")

# fetch API
@app.route("/word_list/", methods=["GET"])
def get_word_list():
    all_record = WordList.query.order_by(WordList.id).all()
    top_data = []
    for record in all_record:
        top_data.append({
            "id":record.id,
            "category":record.category,
            "enWord":record.en_word,
            # 意味を分割して配列に変換
            "jaMeaning":re.split("[；，]", record.ja_meaning)
        })
    return jsonify({"top":top_data})

# 末尾に/を付けると、リダイレクトされてしまいステータスコードが変わるので注意
@app.route("/word/<id>", methods=["PUT"])
def change_category(id):
    word = WordList.query.filter_by(id=id).first()
    # application/json の場合
    word.category = request.json["nextCategory"]
    db.session.add(word)
    db.session.commit()
    return "", 200
    
if __name__ == "__main__":
    # 最後に消す!!!
    # app.debug = True
    app.run(host="0.0.0.0") 
