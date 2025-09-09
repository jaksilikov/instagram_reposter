import os
import time
import logging
from instagrapi import Client

class InstagramReposter:
    def __init__(self, cl: Client, source_username: str, downloads_folder: str,
                 posted_file: str, media_amount: int = 10, sleep_seconds: int = 10, log_file: str = None):
        self.cl = cl
        self.source_username = source_username
        self.downloads_folder = downloads_folder
        self.posted_file = posted_file
        self.media_amount = media_amount
        self.sleep_seconds = sleep_seconds

        # Логирование
        os.makedirs(os.path.dirname(log_file), exist_ok=True) if log_file else None
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

        # Создаем папку для скачанных файлов
        os.makedirs(self.downloads_folder, exist_ok=True)

        # Загружаем список опубликованных постов
        if os.path.exists(self.posted_file):
            with open(self.posted_file, "r") as f:
                self.posted_ids = set(f.read().splitlines())
        else:
            self.posted_ids = set()

        # Получаем ID пользователя
        self.user_id = self.cl.user_id_from_username(self.source_username)

    def fetch_posts(self):
        try:
            raw_medias = self.cl.user_medias(self.user_id, amount=self.media_amount)
            medias = [m for m in raw_medias if not getattr(m, "is_pinned", False)]
            self.logger.info(f"Загружено {len(medias)} постов с аккаунта {self.source_username}")
            return medias
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке постов: {e}")
            return []

    def repost(self):
        medias = self.fetch_posts()
        for media in medias:
            if str(media.pk) in self.posted_ids:
                self.logger.info(f"⏩ Пропущен (уже опубликован): {media.pk}")
                continue
            try:
                if media.media_type == 1:  # Фото
                    path = self.cl.photo_download(media.pk, self.downloads_folder)
                    self.cl.photo_upload(path, caption=media.caption_text)

                elif media.media_type == 2:  # Видео
                    path = self.cl.video_download(media.pk, self.downloads_folder)
                    self.cl.video_upload(path, caption=media.caption_text)

                elif media.media_type == 8:  # Альбом
                    paths = self.cl.album_download(media.pk, self.downloads_folder)
                    self.cl.album_upload(paths, caption=media.caption_text)

                # Сохраняем ID
                with open(self.posted_file, "a") as f:
                    f.write(str(media.pk) + "\n")
                self.posted_ids.add(str(media.pk))

                self.logger.info(f"✅ Скопирован пост: {media.pk}")
                time.sleep(self.sleep_seconds)
            except Exception as e:
                self.logger.error(f"❌ Ошибка с постом {media.pk}: {e}")
