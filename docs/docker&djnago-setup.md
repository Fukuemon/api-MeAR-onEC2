# Dockerコンテナ準備
## 1. Dockerfile作成
docker run build時に実行されるスクリプト
```Dockerfile
FROM python:3.9 //python3.9のDockerイメージ取得
ENV PYTHONUNBUFFERED 1 //
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000
```
説明
```Dockerfile
ENV PYTHONUNBUFFERED 1
PythonがI/Oをバッファリングしないように設定。
→ログメッセージなどがリアルタイムでコンソールに表示されるようにする

WORKDIR /app
Dockerコンテナ内の作業ディレクトリを/appに設定

COPY requirements.txt /app/requirements.txt
ホストマシンのrequirements.txtファイルを、コンテナ内の/app/requirements.txtにコピーする
(後述で、このプロジェクトで使うライブラリ群をインストールするためのファイルを作成する)

RUN pip install -r requirements.txt
コマンドを実行：requirements.txtにリストされているPythonのパッケージをインストール

COPY . /app
ホストマシンのディレクトリ内容をコンテナないの/appディレクトリにコピー

EXPOSE 8000
コンテナのポートを公開して、アクセスできるように

CMD python manage.py runserver 0.0.0.0:8000
コンテナが起動されたらコマンド実行：サーバー立ち上げ
```

## 2. docker-compose.ymlファイル作成
複数のコンテナをまとめて管理・実行するための設定ファイル
ここに記されたコンテナを`Docker ccomposeコマンド`で管理できるようになる
```yml
version: '3.8'
services:
  backend:
    container_name: django-container
    build: .
    volumes:
      - .:/app
    ports:
        - "8000:8000"
    depends_on:
        - db
  db:
    container_name: postgres-container
    image: postgres
    restart: always
    environment:
      - POSTGRES_DB=django
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgresdb:/var/lib/postgresql
volumes:
  postgresdb:
```

```yml
version: '3.8'
// 使用するDocker Composeのファイルフォーマットのバージョンを指定

services:
//このセクションの中に、起動する(サービス)コンテナの設定を記述していく

  backend:
    container_name: django-container
    // コンテナの名前：django-container

    build: .
   // カレントディレクトリ（.）のDockerfileを使用してイメージをビルドする

    volumes:
      - .:/app
     // ホストの現在のディレクトリをコンテナの/appディレクトリにマウント


    ports:
        - "8000:8000"
     // ホストの8000番ポートをコンテナの8000番ポートにマッピング


    depends_on:
        - db
    // dbサービスが先に起動されるように設定


  db:
    container_name: postgres-container
    image: postgres
    // 公式のpostgresイメージを指定

    restart: always
    // コンテナが停止した場合、常に再起動するように設定

    environment:
    // PostgreSQLの環境変数を設定(データベース名、ユーザー名、パスワードを指定)

      - POSTGRES_DB=django
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgresdb:/var/lib/postgresql
    //  postgresdbという名前のボリュームをコンテナの/var/lib/postgresqlディレクトリにマウント

volumes:
  postgresdb:
// postgresdbという名前のボリュームをコンテナの/var/lib/postgresqlディレクトリにマウント

```

## 3. requirements.txtにインストールするパッケージを記載

```
Django==4.2.2
django-cors-headers==4.1.0
djangorestframework==3.14.0
Pillow==10.0.0
djangorestframework-simplejwt==5.2.2
drf-yasg==1.21.7
psycopg==3.1 //
python-decouple==3.8 //環境変数の設定を行うパッケージ
```

## 4, コンテナ立ち上げ

```
docker-compose build
```

完了

# Djngoプロジェクト立ち上げ

## 1. 設定用のプロジェクト作成
```
docker-compose run backend django-admin startproject config .
```
補足：先ほど作成したサービス内で、djangoプロジェクトを立ち上げるコマンドを実行
`.`を忘れないようにする！

`.` ：カレントディレクトリに直接プロジェクトが作成される

## 2. settings.pyのSECRET_KEYを環境変数で管理
### 環境変数に設定
.envファイルを作成
```
.
├── .env
├── config
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```
settings.pyにある .envファイルにシークレットキーを記入
```txt
SECRET_KEY={YOUR_SECRET_KEY}
```
settings.pyで環境変数を読み込む

```python
from decouple import config
SECRET_KEY = config('SECRET_KEY')
```
これで設定完了！

## 3. settigs.pyの編集

INSTALLED_APPS

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
		# ここから追加
    'rest_framework',
    'rest_framework_simplejwt', //Django Rest FrameworkでJSON Web Tokens (JWT) 認証を実装する
    'drf_yasg', //OpenAPI/Swaggerの仕様に基づいてAPIのドキュメントを生成する
    'rest_framework_simplejwt token_blacklist', //JWTトークンのブラックリスト機能を実装する
]
```

MIDDLEWARE

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', //追加
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

DATABASE

postgresssqlに変更する

```python
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': config("DB_HOST"),
        'PORT': config("DB_PORT"),
    }
}
```

.envに環境変数

```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME=django
DB_USER=username
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```

日本語設定

```python
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
```

メディアファイルのpath設定

```python
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
```

CORSの設定

```python
# CORS
CORS_ALLOWED_ORIGINS = {
    "http://localhost:3000",
    "http://localhost:8000",
}

CORS_ALLOWED_WHITELIST = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

JWTの設定

```python
# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1), #Tokenの有効期限
    'ROTATE_REFRESH_TOKENS': True, #
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('JWT',),
}
```

RestFramework

```python
# DRF
REST_FRAMEWORK = {
    # viewを特定のユーザにだけ見せるようにする
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # 認証方法を指定する
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ]
}
```
設定完了