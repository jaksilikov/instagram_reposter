import json
from instagrapi import Client

def login_and_save_session(username: str, password: str, session_file: str = "session.json") -> Client:
    """
    Авторизация в Instagram и сохранение сессии
    """
    cl = Client()
    cl.login(username, password)
    cl.dump_settings(session_file)
    print(f"✅ Авторизация прошла успешно, сессия сохранена в {session_file}")
    return cl

def load_session(session_file: str = "session.json") -> Client:
    """
    Загрузка сессии из файла
    """
    cl = Client()
    with open(session_file, "r") as f:
        cl.set_settings(json.load(f))
    return cl
