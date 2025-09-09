import json
import os
from auth import login_and_save_session, load_session
from reposter import InstagramReposter
from instagrapi import Client

# Загружаем настройки
with open("config.json", "r") as f:
    config = json.load(f)

# Загрузка сессии или авторизация
cl: Client
if os.path.exists("session.json"):
    try:
        cl = load_session("session.json")
        cl.get_timeline_feed()
        print("✅ Сессия загружена")
    except Exception:
        print("⚠️ Сессия не действительна, выполняется логин")
        cl = login_and_save_session(config["username"], config["password"])
else:
    cl = login_and_save_session(config["username"], config["password"])

# Создаем репостер
reposter = InstagramReposter(
    cl=cl,
    source_username=config["source_username"],
    downloads_folder=config["downloads_folder"],
    posted_file=config["posted_file"],
    media_amount=config.get("media_amount", 10),
    sleep_seconds=config.get("sleep_seconds", 10),
    log_file=config.get("log_file", "logs/reposter.log")
)

# Запуск репоста
reposter.repost()
