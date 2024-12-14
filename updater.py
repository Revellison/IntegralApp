import os
import requests
import zipfile
import shutil
import sys

class AutoUpdater:
    def __init__(self, repo_url, download_dir="updates"):
        """
        :param repo_url: Ссылка на репозиторий GitHub
        :param download_dir: Папка для загрузки обновлений
        """
        self.repo_url = repo_url
        self.download_dir = download_dir
        self.latest_release_url = f"{self.repo_url}/releases/latest"
        self.update_zip_path = os.path.join(self.download_dir, "update.zip")
        self.app_dir = os.path.dirname(os.path.abspath(__file__))

    def get_latest_release(self):
        """Получение информации о последнем релизе"""
        response = requests.get(self.latest_release_url)
        if response.status_code == 200:
            release_data = response.json()
            return release_data.get("zipball_url"), release_data.get("name")
        else:
            raise Exception("Не удалось получить последний релиз.")

    def download_update(self, download_url):
        """Скачивание обновления"""
        os.makedirs(self.download_dir, exist_ok=True)
        with requests.get(download_url, stream=True) as response:
            response.raise_for_status()
            with open(self.update_zip_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

    def extract_update(self):
        """Распаковка обновления"""
        with zipfile.ZipFile(self.update_zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.download_dir)

    def apply_update(self):
        """Копирование файлов обновления"""
        extracted_folder = next(
            os.path.join(self.download_dir, d)
            for d in os.listdir(self.download_dir)
            if os.path.isdir(os.path.join(self.download_dir, d))
        )
        for root, dirs, files in os.walk(extracted_folder):
            for file in files:
                source = os.path.join(root, file)
                relative_path = os.path.relpath(source, extracted_folder)
                destination = os.path.join(self.app_dir, relative_path)
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.move(source, destination)

    def cleanup(self):
        """Удаление временных файлов"""
        shutil.rmtree(self.download_dir, ignore_errors=True)

    def update(self):
        """Основной процесс обновления"""
        try:
            print("Получение последнего релиза...")
            download_url, version = self.get_latest_release()
            print(f"Последняя версия: {version}")
            print("Загрузка обновления...")
            self.download_update(download_url)
            print("Распаковка обновления...")
            self.extract_update()
            print("Применение обновления...")
            self.apply_update()
            print("Очистка временных файлов...")
            self.cleanup()
            print("Обновление завершено!")
        except Exception as e:
            print(f"Ошибка обновления: {e}")
            self.cleanup()

if __name__ == "__main__":
    repo_url = "https://api.github.com/repos/Revellison/IntegralApp"
    updater = AutoUpdater(repo_url)
    updater.update()
