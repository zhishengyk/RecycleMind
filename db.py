import pymysql

DB_CONFIG = {
    "host": "39.106.228.80",  # 确认此IP为你的ECS公网IP
    "port": 3306,  # 修正为MySQL默认端口
    "user": "root",           # 通常为root，不要加@localhost
    "password": "Test@114514",
    "database": "recycle_mind",
    "charset": "utf8mb4",
    "autocommit": True
}

def get_db_conn():
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"数据库连接失败: {e}")
        raise
