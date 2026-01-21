# update_db.py

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Завантажуємо змінні середовища, щоб отримати доступ до DATABASE_URL
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
            print("🛠 Перевірка та додавання стовпця 'delivery_zones_content'...")
            
            # SQL-команда, яка додає стовпець, якщо його ще немає
            # IF NOT EXISTS гарантує, що помилки не буде, якщо ви запустите скрипт двічі
            sql_command = text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS delivery_zones_content TEXT;")
            
            await conn.execute(sql_command)
            print("✅ Успішно! Стовпець 'delivery_zones_content' додано до таблиці 'settings'.")
            
    except Exception as e:
        print(f"❌ Виникла помилка при оновленні бази даних: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    # Запускаємо асинхронну функцію
    if os.name == 'nt':  # Для Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_database())