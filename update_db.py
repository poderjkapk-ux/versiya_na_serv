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
            
            # --- 1. Оновлення таблиці SETTINGS ---
            print(" -> Оновлення таблиці 'settings'...")
            
            try:
                await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS site_header_text VARCHAR(100);"))
                print("    ✅ Стовпець 'site_header_text' додано.")
            except Exception as e: pass

            try:
                await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS google_analytics_id VARCHAR(50);"))
                print("    ✅ Стовпець 'google_analytics_id' додано.")
            except Exception as e: pass

            try:
                await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS delivery_zones_content TEXT;"))
                print("    ✅ Стовпець 'delivery_zones_content' додано.")
            except Exception as e: pass

            # Нові поля для SEO шаблонів
            try:
                await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS product_seo_mask_title VARCHAR(255) DEFAULT '{name} - {price} грн | {site_title}';"))
                print("    ✅ Стовпець 'product_seo_mask_title' додано.")
            except Exception as e: 
                print(f"    ⚠️ Помилка (product_seo_mask_title): {e}")

            try:
                await conn.execute(text("ALTER TABLE settings ADD COLUMN IF NOT EXISTS product_seo_mask_desc VARCHAR(500) DEFAULT '{name} - {description}. Ціна: {price} грн.';"))
                print("    ✅ Стовпець 'product_seo_mask_desc' додано.")
            except Exception as e: 
                print(f"    ⚠️ Помилка (product_seo_mask_desc): {e}")


            # --- 2. Оновлення таблиці PRODUCTS ---
            print(" -> Оновлення таблиці 'products'...")
            
            # Нові поля для індивідуального SEO товарів
            try:
                await conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS seo_title VARCHAR(255);"))
                print("    ✅ Стовпець 'seo_title' додано до products.")
            except Exception as e: 
                print(f"    ⚠️ Помилка (seo_title): {e}")

            try:
                await conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS seo_description_meta VARCHAR(500);"))
                print("    ✅ Стовпець 'seo_description_meta' додано до products.")
            except Exception as e: 
                print(f"    ⚠️ Помилка (seo_description_meta): {e}")
            
            print("\n✅ Усі операції з оновлення бази даних завершено успішно.")
            
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