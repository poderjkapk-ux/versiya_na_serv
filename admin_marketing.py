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
    
    # Получаем первый попап (будем использовать один редактируемый)
    result = await session.execute(select(MarketingPopup).limit(1))
    popup = result.scalars().first()
    
    if not popup:
        # Создаем пустой объект для шаблона, если в БД нет записи
        popup = MarketingPopup(title="", content="", button_text="", button_link="", is_active=False, show_once=True)

    current_image_html = ""
    if popup.image_url:
        current_image_html = f'<div style="margin: 10px 0;"><img src="/{popup.image_url}" style="max-height: 150px; border-radius: 8px;"></div>'

    body = ADMIN_MARKETING_BODY.format(
        popup_id=popup.id if popup.id else "new",
        title=html.escape(popup.title or ""),
        content=html.escape(popup.content or ""),
        current_image_html=current_image_html,
        button_text=html.escape(popup.button_text or ""),
        button_link=html.escape(popup.button_link or ""),
        is_active_checked="checked" if popup.is_active else "",
        show_once_checked="checked" if popup.show_once else ""
    )
    
    active_classes = {key: "" for key in ["main_active", "orders_active", "clients_active", "tables_active", "products_active", "categories_active", "menu_active", "employees_active", "statuses_active", "reports_active", "settings_active", "design_active", "inventory_active"]}
    # Добавим класс marketing_active (нужно будет добавить ссылку в меню, но пока используем settings как базу или reports)
    active_classes["settings_active"] = "active" 

    return HTMLResponse(ADMIN_HTML_TEMPLATE.format(
        title="Маркетинг", 
        body=body, 
        site_title=settings.site_title or "Назва",
        **active_classes
    ))

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
    
    # Обработка изображения
    if image_file and image_file.filename:
        # Удаляем старое, если было
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