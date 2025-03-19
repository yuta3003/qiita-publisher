import os
import json
import requests
import glob
import yaml

# Qiita APIのエンドポイント
QIITA_API_URL = "https://qiita.com/api/v2/items"

# Qiitaトークンを環境変数から取得
QIITA_TOKEN = os.getenv("QIITA_TOKEN")
if not QIITA_TOKEN:
    raise ValueError("Qiita APIトークンが設定されていません")

# 投稿するMarkdownファイルのあるフォルダ
ARTICLE_DIR = "articles"

# 記事IDを保存するJSONファイル
QIITA_ID_FILE = ".github/qiita_posted.json"

# 記事IDの読み込み
if os.path.exists(QIITA_ID_FILE):
    with open(QIITA_ID_FILE, "r", encoding="utf-8") as f:
        qiita_ids = json.load(f)
else:
    qiita_ids = {}

def parse_markdown(file_path):
    """Markdown ファイルから Front Matter (YAML) を解析し、本文を取得"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        meta_data = yaml.safe_load(parts[1])
        body = parts[2].strip()
    else:
        meta_data = {}
        body = content

    return meta_data, body

# `.md` ファイルを取得
md_files = glob.glob(f"{ARTICLE_DIR}/*.md")

for md_file in md_files:
    file_name = os.path.basename(md_file)  # 記事IDの管理に使うキー
    meta, body = parse_markdown(md_file)

    title = meta.get("title", file_name.replace(".md", "").replace("_", " ").title())
    tags = [{"name": tag} for tag in meta.get("tags", [])]
    private = meta.get("private", False)

    # 投稿データ
    data = {
        "title": title,
        "body": body,
        "private": private,
        "tags": tags
    }

    if file_name in qiita_ids:
        # 記事IDがある場合は更新
        qiita_article_id = qiita_ids[file_name]
        response = requests.put(
            f"{QIITA_API_URL}/{qiita_article_id}",
            headers={"Authorization": f"Bearer {QIITA_TOKEN}"},
            json=data
        )
        action = "更新"
    else:
        # 記事IDがない場合は新規投稿
        response = requests.post(
            QIITA_API_URL,
            headers={"Authorization": f"Bearer {QIITA_TOKEN}"},
            json=data
        )
        action = "新規投稿"

        # 新規投稿に成功したら記事IDを保存
        if response.status_code == 201:
            qiita_ids[file_name] = response.json().get("id")

    # 結果の確認
    if response.status_code in [200, 201]:
        print(f"Qiita {action}成功: {title}")
        print("記事URL:", response.json().get("url"))
    else:
        print(f"Qiita {action}失敗: {title}")
        print("エラー:", response.text)

# 記事IDの保存
with open(QIITA_ID_FILE, "w", encoding="utf-8") as f:
    json.dump(qiita_ids, f, indent=2, ensure_ascii=False)
