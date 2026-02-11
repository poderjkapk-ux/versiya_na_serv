# fix_db.py

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Завантажуємо змінні
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL не знайдено в .env!")
    exit(1)

# ВАЖЛИВО: isolation_level="AUTOCOMMIT" гарантує, що зміни застосуються миттєво
engine = create_async_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")

async def fix_database():
    print(f"🔧 Підключення до бази даних...")
    
    async with engine.connect() as conn:
        # 1. Перевіряємо, які колонки ВЖЕ є в базі
        print("🔍 Перевірка існуючих колонок у таблиці settings...")
        try:
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='settings';"
            ))
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"📄 Знайдені колонки: {existing_columns}")
        except Exception as e:
            print(f"❌ Помилка при читанні структури таблиці: {e}")
            return

        # 2. Список колонок, які треба додати
        columns_to_add = [
            ("google_ads_id", "VARCHAR(50)"),
            ("google_ads_conversion_label", "VARCHAR(100)"),
            ("google_analytics_id", "VARCHAR(50)"),
            ("site_header_text", "VARCHAR(100)"),
            ("delivery_zones_content", "TEXT"),
            ("product_seo_mask_title", "VARCHAR(255)"),
            ("product_seo_mask_desc", "VARCHAR(500)"),
        ]

        # 3. Додаємо тільки ті, яких немає
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"➕ Додаємо колонку {col_name}...")
                try:
                    await conn.execute(text(f"ALTER TABLE settings ADD COLUMN {col_name} {col_type}"))
                    print(f"✅ {col_name} успішно додано.")
                except Exception as e:
                    # Ігноруємо помилку "вже існує", якщо раптом виникне гонка
                    if "already exists" in str(e):
                        print(f"ℹ️ {col_name} вже існує (помилка SQL).")
                    else:
                        print(f"⚠️ Помилка при додаванні {col_name}: {e}")
            else:
                print(f"ℹ️ Колонка {col_name} вже існує.")

    await engine.dispose()
    print("🏁 Діагностика та ремонт завершені.")

if __name__ == "__main__":
    asyncio.run(fix_database())