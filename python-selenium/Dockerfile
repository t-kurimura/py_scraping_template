FROM python:3.9

# vimとseleniumをインストール
RUN set -x && \
  apt-get update && \
  apt-get install -y vim && \
  pip install  \
    selenium==4.8.2 \
    webdriver-manager==3.8.5 \
    firebase-admin==6.1.0 \
    python-dotenv==1.0.0 \
    google-cloud-logging==3.5.0

# cronをインストール
RUN apt-get update && apt-get -y install cron

# crontabファイルをコピー
COPY crontab /etc/cron.d/my-cron-job

# crontabファイルのパーミッションを設定
RUN chmod 0644 /etc/cron.d/my-cron-job