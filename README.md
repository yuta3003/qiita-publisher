# Qiita Auto Publisher

GitHub Actions を使って、GitHub リポジトリから Qiita に記事を **自動投稿・更新** するワークフローです。

## 🚀 特徴
- `articles/` フォルダ内の Markdown (`.md`) を自動投稿
- 記事を **新規投稿** または **更新** 可能
- Qiita の記事 ID をリポジトリで管理
- GitHub Actions で **push するだけで Qiita に反映**

## 📂 フォルダ構成

```
├── articles/                 # Qiita に投稿する記事フォルダ
│   ├── example.md            # 記事ファイル (Qiita に投稿・更新)
│   ├── tutorial.md           # 記事ファイル (Qiita に投稿・更新)
├── .github/
│   ├── workflows/
│   │   ├── qiita-publish.yml # GitHub Actions の設定ファイル
│   ├── scripts/
│   │   ├── publish_to_qiita.py # Qiita 投稿スクリプト
├── .github/qiita_posted.json  # 記事 ID 管理 (自動生成)
├── README.md                  # このリポジトリの説明
```

## 📝 記事のテンプレート (`articles/example.md`)
Qiita に投稿する記事は、以下のテンプレート形式で記述できます。

```md
---
title: "GitHub Actions で Qiita に自動投稿する"
tags: ["GitHubActions", "Qiita", "Automation"]
private: false
---

# GitHub Actions で Qiita に自動投稿する

この記事では、GitHub Actions を使って Qiita に記事を自動投稿する方法を解説します。

## 1. 必要な準備
- Qiita の API トークン取得
- GitHub Secrets に登録

## 2. 記事を作成
`articles/` に `.md` ファイルを作成

## 3. push するだけ！
GitHub に push すれば自動で Qiita に投稿・更新されます。
```

## 🔧 セットアップ

### 1️⃣ **Qiita API トークンを取得**
[Qiitaの個人設定](https://qiita.com/settings/applications) でアクセストークンを発行。
- 必要な権限: `read_qiita` / `write_qiita`

### 2️⃣ **GitHub Secrets に Qiita トークンを追加**
リポジトリの `Settings > Secrets and variables > Actions` で `QIITA_TOKEN` を追加。

### 3️⃣ **GitHub Actions の設定を確認**
`.github/workflows/qiita-publish.yml` に以下の設定があります。

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

### 4️⃣ **記事を書いて push するだけ！**
- `articles/` フォルダに `.md` ファイルを作成
- `git push` すれば **Qiita に投稿・更新** されます

## 📌 注意点
- Qiita の **記事 ID を `.github/qiita_posted.json` に保存** し、次回以降の更新時に使用します。
- `tags` は **最大5つ** まで指定できます。
- **`private: true` にすると下書き投稿** になります。

## 🎉 クレジット
- [Qiita API ドキュメント](https://qiita.com/api/v2/docs)
- [GitHub Actions](https://docs.github.com/ja/actions)
