from db import get_db_conn
import traceback

def test_db_connection():
    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"当前连接的数据库: {db_name}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("\n数据库中的表:")
            for table in tables:
                print(f"- {table[0]}")
        conn.close()
        print("\n数据库连接测试成功！")
    except Exception as e:
        print(f"\n数据库连接测试失败: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()

def test_user_auth(username, password):
    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, role, email 
                FROM users 
                WHERE username = %s AND password = %s AND is_active = TRUE
            """, (username, password))
            user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            print(f"\n用户认证成功!")
            print(f"用户信息: id={user_data[0]}, username={user_data[1]}, role={user_data[2]}")
            return True
        else:
            print(f"\n用户认证失败: 用户名或密码错误")
            return False
    except Exception as e:
        print(f"\n用户认证测试失败: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 开始测试 ===\n")
    
    # 测试数据库连接
    print("1. 测试数据库连接")
    test_db_connection()
    
    # 测试用户认证
    print("\n2. 测试用户认证")
    # 测试管理员账号
    print("\n测试管理员账号:")
    test_user_auth("admin", "114514")
    
    # 测试普通用户账号
    print("\n测试普通用户账号:")
    test_user_auth("admin1", "114514")
    
    # 测试错误密码
    print("\n测试错误密码:")
    test_user_auth("admin", "wrong_password") 