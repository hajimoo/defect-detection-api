import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# アプリ全体で使うDBコネクションプール
connection_pool = MySQLConnectionPool(
    pool_name="defect_detection_pool",
    pool_size=5,
    pool_reset_session=True,
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)


def get_connection():
    """
    コネクションプールから接続を取得する。

    毎回 mysql.connector.connect() を実行すると、
    接続作成コストが毎回発生して非効率になる。
    そのため、あらかじめ作成した接続を再利用する。
    """
    return connection_pool.get_connection()
