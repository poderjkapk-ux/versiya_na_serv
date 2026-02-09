# update_db.py

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

async def fix_database():
    if not DATABASE_URL:
        print("❌ Помилка: Змінна DATABASE_URL не знайдена в .env файлі.")
        return

    print(f"🔄 Підключення до бази даних...")
    
    # Створюємо двигун
    engine = create_async_engine(DATABASE_URL)

    try:
        async with engine.begin() as conn:
            print("🛠 Перевірка та оновлення структури бази даних...")
            
            # 1. Додаємо google_analytics_id
            print(" -> Додавання стовпця 'google_analytics_id'...")
            await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS google_analytics_id VARCHAR(50);"))
            
            # 2. Додаємо delivery_zones_content (на випадок, якщо його немає)
            print(" -> Додавання стовпця 'delivery_zones_content'...")
            await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS delivery_zones_content TEXT;"))
            
            print("✅ Успішно! Базу даних оновлено.")
            
    except Exception as e:
        print(f"❌ Виникла помилка при оновленні бази даних: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    # Для Windows фікс EventLoop
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_database())