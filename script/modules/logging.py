import logging
from datetime import datetime

from google.cloud import logging as cloud_logging


def setup_logger(label: dict):
    # Cloud Logging クライアントを作成します
    client = cloud_logging.Client()

    # Pythonの標準ログハンドラーに Cloud Logging ハンドラーを追加します
    handler = cloud_logging.handlers.CloudLoggingHandler(
        client=client,
        name=datetime.now().strftime('%Y%m%d%H%M%S'),
        labels=label
    )
    handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)

    # StreamHandler を作成して標準出力に設定
    log_format = "%(asctime)s %(levelname)s %(message)s"
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # すべてのログレベルを表示
    stream_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_handler)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.root.setLevel(logging.DEBUG)
