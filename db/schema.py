from .database import get_db_connection

def create_tables():
    """Barcha kerakli jadvallarni yaratish"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Users jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                full_name VARCHAR(255),
                username VARCHAR(255),
                phone VARCHAR(20) DEFAULT NULL,
                start_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Channels jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id BIGINT PRIMARY KEY,
                name VARCHAR(255),
                type ENUM('channel', 'group') NOT NULL,
                invite_link VARCHAR(255),
                price_1 DECIMAL(10, 2) DEFAULT 0,
                price_3 DECIMAL(10, 2) DEFAULT 0,
                price_12 DECIMAL(10, 2) DEFAULT 0,
                status TINYINT DEFAULT 1
            )
        """)

        # 3. Subscriptions jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                channel_id BIGINT,
                subscription_type TINYINT,
                paid_amount DECIMAL(10, 2),
                start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_date DATETIME,
                status TINYINT DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE
            )
        """)

        # 4. Settings jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key_name VARCHAR(255) PRIMARY KEY,
                value_text TEXT
            )
        """)
        conn.commit()
        print("Baza jadvallari muvaffaqiyatli tekshirildi.")
    except Exception as e:
        print(f"Jadval yaratishda xato: {e}")
    finally:
        cursor.close()
        conn.close()