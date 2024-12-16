import os
import tarfile
import requests
import json
import shutil
from packaging import version

def get_current_version():
    """Чтение текущей версии приложения из файла."""
    version_file = "version.json"
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    return "0.0.0"

def get_latest_version_info(repo_url):
    """Получение информации о последней версии из GitHub."""
    releases_api_url = f"{repo_url}/releases/latest"
    response = requests.get(releases_api_url)
    if response.status_code == 200:
        release_info = response.json()
        return release_info.get("tag_name"), release_info.get("tarball_url")
    else:
        raise Exception(f"Failed to fetch latest version info: {response.status_code}")

def download_and_extract_tarball(url, extract_to):
    """Скачивание и распаковка .tar архива."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        tarball_path = "latest.tar.gz"
        with open(tarball_path, "wb") as f:
            f.write(response.content)

        # Распаковка архива
        with tarfile.open(tarball_path, "r:gz") as tar:
            tar.extractall(extract_to)

        os.remove(tarball_path)  # Удаление архива после распаковки

        # Определяем корневую папку внутри архива
        extracted_dirs = [
            name for name in os.listdir(extract_to)
            if os.path.isdir(os.path.join(extract_to, name))
        ]

        if len(extracted_dirs) == 1:
            return os.path.join(extract_to, extracted_dirs[0])
        else:
            raise Exception("Не удалось определить корневую папку архива.")

    else:
        raise Exception(f"Failed to download tarball: {response.status_code}")

def backup_and_replace(src, dst, backup_dir):
    """Сохранение текущей версии файлов и замена."""
    if os.path.exists(dst):
        # Создание директории для бэкапа, если её нет
        os.makedirs(backup_dir, exist_ok=True)

        # Путь для сохранения бэкапа
        backup_path = os.path.join(backup_dir, os.path.basename(dst))

        if os.path.isdir(dst):
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(dst, backup_path)
        else:
            shutil.copy2(dst, backup_path)

        print(f"Бэкап сделан: {backup_path}")

        if os.path.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)

    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

def update_application(repo_url):
    """Основная функция обновления приложения."""
    temp_dir = None  # Инициализация переменной
    backup_dir = "updatelocalhistory"  # Директория для сохранения бэкапов
    try:
        print("Checking for updates...")

        # Получение текущей версии
        current_version = get_current_version()
        print(f"Current version: {current_version}")

        # Получение информации о последней версии
        latest_version, tarball_url = get_latest_version_info(repo_url)
        print(f"Latest version: {latest_version}")

        # Сравнение версий
        if version.parse(current_version) > version.parse(latest_version):
            print("Вы находитесь в тестовой версии приложения.")
            return

        if current_version == latest_version:
            print("Application is up-to-date.")
            return

        print("Downloading the latest version...")

        # Создание временной папки для распаковки
        temp_dir = "temp_update"
        os.makedirs(temp_dir, exist_ok=True)

        extracted_root = download_and_extract_tarball(tarball_url, temp_dir)

        print("Updating application files...")

        # Копирование файлов из корневой папки обновления в текущую директорию с бэкапом заменяемых файлов
        for item in os.listdir(extracted_root):
            s = os.path.join(extracted_root, item)
            d = os.path.join(os.getcwd(), item)
            backup_and_replace(s, d, backup_dir)

        # Обновление версии
        with open("version.json", "w") as f:
            json.dump({"version": latest_version}, f)

        print("Application updated successfully!")

    except Exception as e:
        print(f"Update failed: {e}")

    finally:
        # Удаление временной папки
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    # Замените на URL вашего репозитория
    GITHUB_REPO_URL = "https://api.github.com/repos/Revellison/IntegralApp"

    update_application(GITHUB_REPO_URL)


