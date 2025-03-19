---
title: "GitHubにpushしてQiitaに投稿"
tags: ["GitHubActions", "Qiita", "Automation"]
private: true
---

# GitHubにpushしてQiitaに投稿

GitHubのリポジトリに記事を書いてpushすると、自動でQiitaに投稿・更新される仕組みをGitHub Actionsを使って構築しました。

これにより、**GitHub で記事を管理しつつ、Qiita に自動投稿できる** ようになります！ 🚀

## 🎯 できること
- `articles/` フォルダ内の Markdown (`.md`) を **自動投稿・更新**
- Qiita の記事 ID を **GitHub で管理**
- `git push` するだけで **Qiita に反映**

## 🛠 環境構築

### 1️⃣ **Qiita API トークンを取得**
[Qiitaの個人設定](https://qiita.com/settings/applications) で API トークンを発行します。

必要な権限:
- `read_qiita`（記事の読み取り）
- `write_qiita`（記事の作成・更新）

発行したトークンは、GitHub の **Secrets** に登録します。

### 2️⃣ **GitHub Secrets に Qiita トークンを追加**
GitHub リポジトリの `Settings > Secrets and variables > Actions` で `QIITA_TOKEN` を追加。

## ⚙️ フォルダ構成

```
├── articles/                 # Qiita に投稿する記事フォルダ
│   ├── 2024-03-19-github-to-qiita.md  # 記事ファイル
│   ├── tutorial.md           # 記事ファイル
├── .github/
│   ├── workflows/
│   │   ├── qiita-publish.yml # GitHub Actions の設定
│   ├── scripts/
│   │   ├── publish_to_qiita.py # Qiita 投稿スクリプト
├── .github/qiita_posted.json  # 記事 ID 管理 (自動生成)
├── README.md                  # リポジトリの説明
```

## 🚀 GitHub Actions 設定

`.github/workflows/qiita-publish.yml` に以下を追加。

```yaml
name: Publish to Qiita

on:
  push:
    branches:
      - main  # mainブランチにpushされたときに実行

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
      - name: リポジトリをチェックアウト
        uses: actions/checkout@v4

      - name: Pythonをセットアップ
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: 依存関係をインストール
        run: pip install requests pyyaml

      - name: Qiita に投稿・更新
        env:
          QIITA_TOKEN: ${{ secrets.QIITA_TOKEN }}
        run: python .github/scripts/publish_to_qiita.py
```

## 📝 Qiita 投稿スクリプト

`.github/scripts/publish_to_qiita.py` に Qiita 投稿用のスクリプトを作成。

```python
import os
import requests
import glob
import json
import yaml

QIITA_API_URL = "https://qiita.com/api/v2/items"
QIITA_TOKEN = os.getenv("QIITA_TOKEN")
QIITA_ID_FILE = ".github/qiita_posted.json"
ARTICLE_DIR = "articles"

if not QIITA_TOKEN:
    raise ValueError("Qiita APIトークンが設定されていません")

if os.path.exists(QIITA_ID_FILE):
    with open(QIITA_ID_FILE, "r", encoding="utf-8") as f:
        qiita_ids = json.load(f)
else:
    qiita_ids = {}

def parse_markdown(file_path):
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

md_files = glob.glob(f"{ARTICLE_DIR}/*.md")

for md_file in md_files:
    file_name = os.path.basename(md_file)
    meta, body = parse_markdown(md_file)
    title = meta.get("title", file_name.replace(".md", "").replace("_", " ").title())
    tags = [{"name": tag} for tag in meta.get("tags", [])]
    private = meta.get("private", False)
    data = {"title": title, "body": body, "private": private, "tags": tags}
    if file_name in qiita_ids:
        qiita_article_id = qiita_ids[file_name]
        response = requests.put(f"{QIITA_API_URL}/{qiita_article_id}", headers={"Authorization": f"Bearer {QIITA_TOKEN}"}, json=data)
    else:
        response = requests.post(QIITA_API_URL, headers={"Authorization": f"Bearer {QIITA_TOKEN}"}, json=data)
        if response.status_code == 201:
            qiita_ids[file_name] = response.json().get("id")
    if response.status_code in [200, 201]:
        print(f"投稿成功: {title}")
    else:
        print(f"投稿失敗: {title}")

with open(QIITA_ID_FILE, "w", encoding="utf-8") as f:
    json.dump(qiita_ids, f, indent=2, ensure_ascii=False)
```

## ✅ まとめ
1. Qiita API トークンを取得し、GitHub Secrets に `QIITA_TOKEN` を追加
2. `articles/` に記事を `.md` 形式で作成
3. `git push` するだけで Qiita に **自動投稿 & 更新！**

これで、**GitHub で記事を管理しつつ、Qiita へ簡単に連携できる環境が完成！** 🚀
