# update_db.py

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

async def fix_database():
    if not DATABASE_URL:
        print("❌ Помилка: Змінна DATABASE_URL не знайдена в .env файлі.")
        return

    print(f"🔄 Підключення до бази даних...")
    
    # Створюємо двигун (engine)
    engine = create_async_engine(DATABASE_URL)

    try:
        async with engine.begin() as conn:
            print("🛠 Оновлення структури бази даних...")
            
            # 1. Додаємо нове поле для заголовка в шапці (site_header_text)
            print(" -> Перевірка та додавання стовпця 'site_header_text'...")
            # Використовуємо IF NOT EXISTS (або ігноруємо помилку, якщо колонка є)
            try:
                await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS site_header_text VARCHAR(100);"))
                print("    ✅ Стовпець 'site_header_text' успішно додано (або вже існував).")
            except Exception as e:
                print(f"    ⚠️ Повідомлення: {e}")

            # 2. Додаємо поле для Google Analytics
            print(" -> Перевірка та додавання стовпця 'google_analytics_id'...")
            try:
                await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS google_analytics_id VARCHAR(50);"))
            except Exception as e:
                pass

            # 3. Додаємо поле для зон доставки
            print(" -> Перевірка та додавання стовпця 'delivery_zones_content'...")
            try:
                await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS delivery_zones_content TEXT;"))
            except Exception as e:
                pass
            
            print("\n✅ Усі операції з оновлення бази даних завершено.")
            
    except Exception as e:
        print(f"\n❌ Критична помилка під час оновлення: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    # Налаштування для Windows (якщо сервер на Windows)
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Запуск асинхронної функції
    asyncio.run(fix_database())