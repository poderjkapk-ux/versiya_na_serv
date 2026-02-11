# admin_marketing.py

import os
import secrets
import aiofiles
import html
from typing import Optional

from fastapi import APIRouter, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import MarketingPopup, Settings
from templates import ADMIN_HTML_TEMPLATE, ADMIN_MARKETING_BODY
from dependencies import get_db_session, check_credentials

router = APIRouter()

@router.get("/admin/marketing", response_class=HTMLResponse)
async def get_marketing_page(
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    settings = await session.get(Settings, 1)
    
    # Отримуємо перший попап (будемо використовувати один редагований)
    result = await session.execute(select(MarketingPopup).limit(1))
    popup = result.scalars().first()
    
    if not popup:
        # Створюємо порожній об'єкт для шаблону, якщо в БД немає запису
        popup = MarketingPopup(title="", content="", button_text="", button_link="", is_active=False, show_once=True)

    current_image_html = ""
    if popup.image_url:
        current_image_html = f'<div style="margin: 10px 0;"><img src="/{popup.image_url}" style="max-height: 150px; border-radius: 8px;"></div>'

    # --- БЛОК НАЛАШТУВАНЬ ТРЕКІНГУ (GOOGLE ANALYTICS & ADS) ---
    ga_id_val = html.escape(settings.google_analytics_id or "")
    ads_id_val = html.escape(settings.google_ads_id or "")
    ads_label_val = html.escape(settings.google_ads_conversion_label or "")

    analytics_settings_html = f"""
    <div style="background: white; padding: 25px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 30px;">
        <h3 style="margin-top: 0; margin-bottom: 15px; font-size: 1.2rem; color: #333;">Трекінг та Аналітика</h3>
        <form action="/admin/marketing/save_settings" method="post">
            
            <div style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #333;">Google Analytics 4 (Measurement ID)</label>
                <input type="text" name="google_analytics_id" value="{ga_id_val}" 
                       placeholder="G-XXXXXXXXXX" 
                       style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 1rem; background: #f8fafc;">
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 6px;">
                    Введіть ідентифікатор потоку даних. Залиште поле порожнім, щоб вимкнути відстеження.
                </div>
            </div>

            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #333;">Google Ads ID (Conversion ID)</label>
                <input type="text" name="google_ads_id" value="{ads_id_val}" 
                       placeholder="AW-XXXXXXXXXX" 
                       style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 1rem; background: #f8fafc; margin-bottom: 10px;">
                
                <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #333;">Google Ads Conversion Label</label>
                <input type="text" name="google_ads_conversion_label" value="{ads_label_val}" 
                       placeholder="Наприклад: AbC_xYz123" 
                       style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 1rem; background: #f8fafc;">
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 6px;">
                    Вкажіть Label конверсії "Покупка" (Purchase). Подія буде відправлена ​​автоматично при успішному замовленні.
                </div>
            </div>

            <button type="submit" style="background: #333; color: white; border: none; padding: 12px 24px; border-radius: 10px; cursor: pointer; font-weight: 600; transition: background 0.2s;">
                Зберегти налаштування
            </button>
        </form>
    </div>
    """

    popup_body = ADMIN_MARKETING_BODY.format(
        popup_id=popup.id if popup.id else "new",
        title=html.escape(popup.title or ""),
        content=html.escape(popup.content or ""),
        current_image_html=current_image_html,
        button_text=html.escape(popup.button_text or ""),
        button_link=html.escape(popup.button_link or ""),
        is_active_checked="checked" if popup.is_active else "",
        show_once_checked="checked" if popup.show_once else ""
    )
    
    # Об'єднуємо блоки: спочатку налаштування GA/Ads, потім банер
    full_body = analytics_settings_html + "<h3 style='margin-bottom:15px; font-size:1.2rem;'>Маркетинговий банер (Pop-up)</h3>" + popup_body
    
    active_classes = {key: "" for key in ["main_active", "orders_active", "clients_active", "tables_active", "products_active", "categories_active", "menu_active", "employees_active", "statuses_active", "reports_active", "settings_active", "design_active", "inventory_active"]}
    # Активуємо пункт меню налаштувань (або можна додати окремий для маркетингу)
    active_classes["settings_active"] = "active" 

    return HTMLResponse(ADMIN_HTML_TEMPLATE.format(
        title="Маркетинг", 
        body=full_body, 
        site_title=settings.site_title or "Назва",
        **active_classes
    ))

# --- РОУТ ДЛЯ ЗБЕРЕЖЕННЯ НАЛАШТУВАНЬ ТРЕКІНГУ ---
@router.post("/admin/marketing/save_settings")
async def save_marketing_settings(
    google_analytics_id: str = Form(""),
    google_ads_id: str = Form(""),
    google_ads_conversion_label: str = Form(""),
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    settings = await session.get(Settings, 1)
    if settings:
        # Зберігаємо або NULL, якщо рядок порожній
        settings.google_analytics_id = google_analytics_id.strip() if google_analytics_id.strip() else None
        settings.google_ads_id = google_ads_id.strip() if google_ads_id.strip() else None
        settings.google_ads_conversion_label = google_ads_conversion_label.strip() if google_ads_conversion_label.strip() else None
        
        await session.commit()
    return RedirectResponse(url="/admin/marketing", status_code=303)

@router.post("/admin/marketing/save")
async def save_marketing_popup(
    popup_id: str = Form(...),
    title: str = Form(""),
    content: str = Form(""),
    button_text: str = Form(""),
    button_link: str = Form(""),
    is_active: bool = Form(False),
    show_once: bool = Form(False),
    image_file: UploadFile = File(None),
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    if popup_id == "new" or not popup_id.isdigit():
        popup = MarketingPopup()
        session.add(popup)
    else:
        popup = await session.get(MarketingPopup, int(popup_id))
        if not popup:
            popup = MarketingPopup()
            session.add(popup)
    
    popup.title = title
    popup.content = content
    popup.button_text = button_text
    popup.button_link = button_link
    popup.is_active = is_active
    popup.show_once = show_once
    
    # Обробка зображення
    if image_file and image_file.filename:
        # Видаляємо старе, якщо було
        if popup.image_url and os.path.exists(popup.image_url):
            try: os.remove(popup.image_url)
            except OSError: pass
            
        ext = image_file.filename.split('.')[-1] if '.' in image_file.filename else 'jpg'
        filename = f"popup_{secrets.token_hex(8)}.{ext}"
        fs_path = os.path.join("static", "images", filename)
        
        try:
            async with aiofiles.open(fs_path, 'wb') as f:
                await f.write(await image_file.read())
            popup.image_url = f"static/images/{filename}"
        except Exception as e:
            print(f"Error saving popup image: {e}")

    await session.commit()
    return RedirectResponse(url="/admin/marketing", status_code=303)