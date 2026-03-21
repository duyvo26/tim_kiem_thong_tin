import mysql.connector
from mysql.connector import Error
from app.config import settings
import os


class BaseDB:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host=os.environ["HOST"],
                user=os.environ["USER"],
                password=os.environ["PASSWORD"],
                database=os.environ["DATABASE"],
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("✅ Kết nối thành công!")
        except Error as e:
            print(f"❌ Lỗi kết nối: {e}")
            self.conn = None

    def get_all_pictures(self):
        query = "SELECT * FROM `base`"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("🔒 Đã đóng kết nối.")
