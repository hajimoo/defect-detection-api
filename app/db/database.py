import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# アプリ起動時にコネクションプールを1回だけ作成する
# pool_size は同時に保持しておく接続数の目安
connection_pool = MySQLConnectionPool(
    pool_name="defect_detection_pool",
    pool_size=5,
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)


def get_connection():
    """
    プールからDB接続を1つ取り出して返す関数

    毎回新しい接続を作るのではなく、
    事前に用意した接続を再利用することで
    パフォーマンスと安定性を上げる。
    """
    return connection_pool.get_connection()
