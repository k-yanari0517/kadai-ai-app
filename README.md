画像キャプション生成AI



\-プロジェクト概要-

本プロジェクトでは、アップロードされた画像の内容をAI（Deep Learning）が解析し、

自動で英文キャプションを生成するWebアプリケーションを構築しました。

開発環境から本番環境（AWS EC2）までの一貫したポータビリティを確保するため、DockerおよびDocker Composeを

活用したマルチコンテナ構成を採用しています。



\-システム構成・使用技術-

実務的なWebシステムを意識し、アプリケーションサーバーとデータベースサーバーを分離した構成としています。

* フロントエンド / バックエンド: Python (Flask)

* AIエンジン: Hugging Face ViT-GPT2 モデル（画像解析・文章生成）

* データベース: PostgreSQL 15（データの永続化とスケーラビリティの確保）

* インフラ: AWS EC2 (Ubuntu), Docker, Docker Compose

* WSGIサーバー: Gunicorn（本番環境用）



\-環境構築と起動手順-


１．リポジトリのクローン

git clone https://github.com/k-yanari0517/kadai-ai-app.git

cd kadai



２.コンテナのビルドと起動

docker compose up -d --build



３.アプリケーションへのアクセス

ローカル環境：http://localhost/

リモート環境：http://<割り当てられたIPアドレス>



\-工夫した点-

AIを使った画像キャプションを作ったこと

DockerとEC2を使って誰でも使えるようにしたこと

データベースのコンテナを分離をしたこと





\-苦労した点と解決策-

dockerfileでライブラリのインストールや実行コマンドの書き方が分からなかったので、chatGPTを使って解決した。

AIモデルを含む Docker イメージは容量が大きくなるため、.dockerignore を活用して不要な仮想環境（venv）やキャッシュを除外し、ビルドの効率化を図りました。

データベースとの接続がうまくいかなかったので、chatGPTを使って解決した。

