# 導入手順

この文書は `discordbot-auto-reaction` を新規環境で起動するための手順をまとめたものです。

## 1. 前提条件

以下を用意してください。

- Python 3.11 系
- Discord Bot Token
- MongoDB 接続 URL
- Bot を招待できる Discord サーバー
- Bot に必要な権限を付与できる管理権限

このリポジトリでは `runtime.txt` に `python-3.11.8` が指定されています。

## 2. Discord Developer Portal の設定

### 2.1 Application を作成

1. Discord Developer Portal を開く
2. `New Application` を選択
3. 任意のアプリケーション名を入力して作成
4. 左メニューの `Bot` から Bot を作成
5. Bot Token を取得する

Bot Token は外部へ公開しないでください。GitHub にコミットしてはいけません。

### 2.2 Privileged Gateway Intents

現在の実装では `discord.Intents.all()` を使用します。

`Bot` 設定画面で、少なくとも次を有効にしてください。

- Message Content Intent

運用方針として `Intents.all()` を維持する場合は、必要な Privileged Gateway Intents を Developer Portal 側でも有効化してください。

### 2.3 OAuth2 URL Generator

`OAuth2` → `URL Generator` で次の Scopes を選択します。

- `bot`
- `applications.commands`

Bot Permissions は最低限、次を選択してください。

- View Channels
- Send Messages
- Read Message History
- Add Reactions
- Use External Emojis
- Embed Links
- Use Application Commands

運用上、補完や確認を確実に行うため、対象チャンネルでこれらの権限が deny されていないことを確認してください。

## 3. MongoDB を用意する

MongoDB Atlas などで MongoDB を用意し、接続 URL を取得します。

接続 URL の例です。

```text
mongodb+srv://user:password@example.mongodb.net/?retryWrites=true&w=majority
```

Bot は次のデータベース・コレクションを使用します。

| 項目 | 名称 |
| --- | --- |
| database | `auto_reaction` |
| collection | `emojis` |

明示的にデータベースやコレクションを事前作成しなくても、初回 upsert 時に作成されます。

## 4. リポジトリを準備する

```bash
git clone https://github.com/DiscordBotPortalJP/discordbot-auto-reaction.git
cd discordbot-auto-reaction
```

## 5. Python 仮想環境を作成する

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 6. 依存関係をインストールする

```bash
pip install -r requirements.txt
```

`requirements.txt` には次の依存関係が含まれます。

```text
emoji
discord.py
python-dotenv
motor
Daug==2023.12.9.1
```

## 7. `.env` を作成する

リポジトリ直下に `.env` を作成します。

```env
TOKEN=YOUR_DISCORD_BOT_TOKEN
MONGO_URL=YOUR_MONGODB_CONNECTION_URL
```

`.env` は `.gitignore` により除外されています。誤ってコミットしないでください。

## 8. `constants.py` を作成する

現行実装では `constants.py` が import されますが、リポジトリには含まれていません。
リポジトリ直下に次の内容で作成してください。

```python
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["TOKEN"]
MONGO_URL = os.environ["MONGO_URL"]
```

## 9. `caches.py` を作成する

現行実装では `caches.py` が import されますが、リポジトリには含まれていません。
リポジトリ直下に次の内容で作成してください。

```python
emojis_cache: dict[int, list[str]] = {}
```

## 10. 起動する

```bash
python main.py
```

起動時に次が実行されます。

1. `extensions.auto_reaction` の読み込み
2. `extensions.reaction_listup` の読み込み
3. Discord アプリケーションコマンドの同期
4. MongoDB からリアクション設定を読み込み
5. メモリキャッシュへ設定を展開

## 11. Bot をサーバーへ招待する

OAuth2 URL Generator で生成した URL から、対象サーバーへ Bot を招待します。

招待後、対象チャンネルで Bot に次の権限があることを確認してください。

- チャンネルを見る
- メッセージを送信
- メッセージ履歴を読む
- リアクションを追加
- 外部の絵文字を使用
- 埋め込みリンク
- アプリケーションコマンドを使用

## 12. 動作確認

### 12.1 自動リアクションを設定する

対象チャンネルで、チャンネル管理権限を持つユーザーが次のように投稿します。

```text
@BotName 👍 ✅
```

成功すると、Bot が `自動リアクション設定を追加しました` と返信します。

### 12.2 投稿にリアクションが付くか確認する

同じチャンネルに任意のメッセージを投稿します。
設定した絵文字が自動で付与されれば成功です。

### 12.3 設定確認を実行する

```text
/リアクション設定確認
```

設定済み絵文字が Embed で表示されれば成功です。

### 12.4 設定を解除する

```text
@BotName
```

成功すると、Bot が `自動リアクション設定を解除しました` と返信します。

## 13. Railway での起動例

このリポジトリには `Procfile` があり、内容は次のとおりです。

```Procfile
web: python main.py
```

Railway で運用する場合は、プロジェクトの Variables に次を設定します。

| 変数名 | 内容 |
| --- | --- |
| `TOKEN` | Discord Bot Token |
| `MONGO_URL` | MongoDB 接続 URL |

ただし、この Bot は HTTP サーバーを提供しません。プラットフォームの構成によっては `web` ではなく `worker` プロセスとして扱う方が適切です。

## 14. セットアップ後の確認項目

- Bot がオンラインになっている
- Slash Command が表示される
- Message Context Menu に `リアクション補完` と `リアクション確認` が表示される
- `@BotName 絵文字...` で設定できる
- 新規投稿へ自動リアクションが付く
- MongoDB の `auto_reaction.emojis` に設定が保存される
- Bot 再起動後も設定が復元される

## 15. よくある導入ミス

| 症状 | 主な原因 |
| --- | --- |
| `ModuleNotFoundError: No module named 'constants'` | `constants.py` が未作成 |
| `ModuleNotFoundError: No module named 'caches'` | `caches.py` が未作成 |
| Bot がメンション設定に反応しない | Message Content Intent が無効、またはチャンネル管理権限がない |
| Slash Command が出ない | `applications.commands` Scope なし、同期直後で反映待ち、Bot 再招待が必要 |
| リアクションが付かない | Bot に Add Reactions / Use External Emojis / Read Message History がない |
| MongoDB に保存されない | `MONGO_URL` の誤り、ネットワーク許可、認証失敗 |
