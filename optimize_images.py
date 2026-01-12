import asyncio
import os
import sys
# 1. Спочатку імпортуємо load_dotenv
from dotenv import load_dotenv

# 2. ОДРАЗУ завантажуємо змінні, ДО імпорту models
load_dotenv()

# 3. Імпортуємо моделі
from models import async_session_maker, Product

# --- ВИПРАВЛЕННЯ: Імпортуємо inventory_models, щоб SQLAlchemy побачила клас Modifier ---
import inventory_models 
# -------------------------------------------------------------------------------------

from sqlalchemy import select
from PIL import Image

# Налаштування оптимізації
MAX_SIZE = (800, 800)  # Максимальний розмір
QUALITY = 80           # Якість
TARGET_FORMAT = "WEBP" # Формат

async def optimize_existing_images():
    async with async_session_maker() as session:
        # Отримуємо всі товари, у яких є зображення
        result = await session.execute(select(Product).where(Product.image_url.is_not(None)))
        products = result.scalars().all()
        
        print(f"Знайдено {len(products)} товарів з фото. Починаємо перевірку...")
        
        count = 0
        errors = 0
        skipped = 0

        for product in products:
            # Якщо шлях порожній або файлу немає
            if not product.image_url or not os.path.exists(product.image_url):
                continue
            
            # Якщо файл вже .webp - пропускаємо
            if product.image_url.lower().endswith('.webp'):
                skipped += 1
                continue

            try:
                original_path = product.image_url
                
                # Відкриваємо зображення
                with Image.open(original_path) as img:
                    # Конвертуємо в RGB
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # Змінюємо розмір
                    img.thumbnail(MAX_SIZE)
                    
                    # Формуємо нове ім'я файлу
                    directory = os.path.dirname(original_path)
                    filename_no_ext = os.path.splitext(os.path.basename(original_path))[0]
                    new_filename = f"{filename_no_ext}.webp"
                    new_path = os.path.join(directory, new_filename)
                    
                    # Зберігаємо оптимізовану версію
                    img.save(new_path, format=TARGET_FORMAT, quality=QUALITY, optimize=True)
                
                # Оновлюємо шлях у базі даних
                if new_path != original_path:
                    product.image_url = new_path
                    
                    # Видаляємо старий файл
                    try:
                        os.remove(original_path)
                    except Exception as e:
                        print(f"Увага: Не вдалося видалити старий файл {original_path}: {e}")
                
                count += 1
                print(f"✅ Оптимізовано: {product.name}")
                
            except Exception as e:
                errors += 1
                print(f"❌ Помилка при обробці '{product.name}': {e}")
        
        # Зберігаємо зміни в БД
        await session.commit()
        print("-" * 30)
        print(f"🏁 Готово!")
        print(f"Оптимізовано: {count}")
        print(f"Вже були WebP: {skipped}")
        print(f"Помилок: {errors}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(optimize_existing_images())