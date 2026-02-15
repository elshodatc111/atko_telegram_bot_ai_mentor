import mysql.connector
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """MySQL bazasiga ulanishni yaratish"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# --- Foydalanuvchilar bilan ishlash ---

def add_user(user_id, full_name, username):
    """Yangi foydalanuvchini qo'shish."""
    conn = get_db_connection()
    cursor = conn.cursor()
    is_new = False
    try:
        sql = "INSERT IGNORE INTO users (id, full_name, username) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user_id, full_name, username))
        conn.commit()
        if cursor.rowcount > 0:
            is_new = True
    except Exception as e:
        print(f"Foydalanuvchini qo'shishda xato: {e}")
    finally:
        cursor.close()
        conn.close()
    return is_new


def get_user_phone(user_id):
    """Foydalanuvchi telefon raqamini olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

def update_user_phone(user_id, phone):
    """Foydalanuvchi telefon raqamini yangilash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET phone = %s WHERE id = %s", (phone, user_id))
    conn.commit()
    cursor.close()
    conn.close()

# --- ADMIN PANEL UCHUN FILTRLANGAN FOYDALANUVCHILARNI OLISH ---

def get_all_users():
    """Barcha foydalanuvchilar ID larini olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users")
        return cursor.fetchall() # Natija: [(id1,), (id2,)]
    except Exception as e:
        print(f"Barcha foydalanuvchilarni olishda xato: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_users_with_phone():
    """Telefon raqami bor foydalanuvchilar ID larini olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # phone NULL emas va bo'sh matn bo'lmaganlar
        cursor.execute("SELECT id FROM users WHERE phone IS NOT NULL AND phone != ''")
        return cursor.fetchall()
    except Exception as e:
        print(f"Raqami bor foydalanuvchilarni olishda xato: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_users_without_phone():
    """Start bosgan lekin raqami yo'q foydalanuvchilar ID larini olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # phone NULL yoki bo'sh matn bo'lganlar
        cursor.execute("SELECT id FROM users WHERE phone IS NULL OR phone = ''")
        return cursor.fetchall()
    except Exception as e:
        print(f"Raqami yo'q foydalanuvchilarni olishda xato: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- Dinamik sozlamalar (Settings) ---

def set_setting(key_name, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO settings (key_name, value_text) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE value_text = %s
        """
        cursor.execute(sql, (key_name, value, value))
        conn.commit()
    except Exception as e:
        print(f"Sozlamani saqlashda xato: {e}")
    finally:
        cursor.close()
        conn.close()

def get_setting(key_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value_text FROM settings WHERE key_name = %s", (key_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Sozlamani olishda xato: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# --- Tekshiruv qismi ---

if __name__ == "__main__":
    try:
        conn = get_db_connection()
        if conn.is_connected():
            print("Tabriklayman! MySQL bazasiga ulanish muvaffaqiyatli amalga oshdi. ✅")
            db_info = conn.get_server_info()
            print(f"MySQL server versiyasi: {db_info}")
        conn.close()
    except Exception as e:
        print(f"Xatolik yuz berdi: {e} ❌")