import os
import json
import requests
import glob
import yaml

QIITA_API_URL = "https://qiita.com/api/v2/items"
QIITA_TOKEN = os.getenv("QIITA_TOKEN")
ARTICLE_DIR = "articles"
QIITA_ID_FILE = ".github/qiita_posted.json"

if not QIITA_TOKEN:
    raise ValueError("Qiita APIトークンが設定されていません")

def load_qiita_ids():
    """ 記事IDをJSONファイルから読み込む """
    if os.path.exists(QIITA_ID_FILE):
        with open(QIITA_ID_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_qiita_ids(qiita_ids):
    """ 記事IDをJSONファイルに保存する """
    print(f"QIITA_ID_FILE: {QIITA_ID_FILE}")
    with open(QIITA_ID_FILE, "w", encoding="utf-8") as f:
        json.dump(qiita_ids, f, indent=2, ensure_ascii=False)

def parse_markdown(file_path):
    """ Markdown ファイルの Front Matter を解析し、本文を取得する """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        meta_data = yaml.safe_load(parts[1])
        body = parts[2].strip()
    else:
        meta_data, body = {}, content

    return meta_data, body

def post_to_qiita(file_name, meta, body, qiita_ids):
    """ Qiitaへ記事を投稿または更新する """
    title = meta.get("title", file_name.replace(".md", "").replace("_", " ").title())
    tags = [{"name": tag} for tag in meta.get("tags", [])]
    private = meta.get("private", False)
    data = {"title": title, "body": body, "private": private, "tags": tags}

    headers = {"Authorization": f"Bearer {QIITA_TOKEN}"}

    if file_name in qiita_ids:
        qiita_article_id = qiita_ids[file_name]
        response = requests.put(f"{QIITA_API_URL}/{qiita_article_id}", headers=headers, json=data)
        action = "更新"
    else:
        response = requests.post(QIITA_API_URL, headers=headers, json=data)
        action = "新規投稿"
        if response.status_code == 201:
            qiita_ids[file_name] = response.json().get("id")

    if response.status_code in [200, 201]:
        print(f"Qiita {action}成功: {title}")
        print("記事URL:", response.json().get("url"))
    else:
        print(f"Qiita {action}失敗: {title}")
        print("エラー:", response.text)

def main():
    print("1")
    qiita_ids = load_qiita_ids()
    print("2")
    md_files = glob.glob(f"{ARTICLE_DIR}/*.md")
    print("3")

    for md_file in md_files:
        print("4")
        file_name = os.path.basename(md_file)
        print("5")
        meta, body = parse_markdown(md_file)
        print("6")
        post_to_qiita(file_name, meta, body, qiita_ids)
        print("7")

    print("8")
    save_qiita_ids(qiita_ids)
    print("9")

if __name__ == "__main__":
    main()
