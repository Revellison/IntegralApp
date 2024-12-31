import os
import tarfile
import requests
import json
import shutil
from packaging import version
from PyQt6.QtWidgets import QMessageBox


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
        tag_name = release_info.get("tag_name")
        # Поиск подходящего файла с расширением .tar
        asset_url = None
        for asset in release_info.get("assets", []):
            if asset["name"].endswith(".tar"):  # Укажите нужное расширение файла
                asset_url = asset["browser_download_url"]
                break

        if not asset_url:
            raise Exception("Не найден файл приложения в формате .tar в релизе.")

        return tag_name, asset_url
    else:
        raise Exception(f"Failed to fetch latest version info: {response.status_code}")


def download_and_extract_tarball(url, extract_to):
    """Скачивание и распаковка архива."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        tarball_path = "latest.tar"
        with open(tarball_path, "wb") as f:
            f.write(response.content)

        with tarfile.open(tarball_path, "r:") as tar:
            # Извлечь содержимое архива
            tar.extractall(extract_to)

        os.remove(tarball_path)

        # Проверить, какие файлы или папки извлеклись
        extracted_items = os.listdir(extract_to)

        # Если в архиве только одна папка, использовать её как корневую
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(extract_to, extracted_items[0])):
            return os.path.join(extract_to, extracted_items[0])
        else:
            # Если несколько файлов/папок, оставить всё как есть
            return extract_to
    else:
        raise Exception(f"Failed to download tarball: {response.status_code}")



def backup_and_replace(src, dst, backup_dir):
    """Сохранение текущей версии файлов и замена."""
    if os.path.exists(dst):
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, os.path.basename(dst))

        if os.path.isdir(dst):
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(dst, backup_path)
        else:
            shutil.copy2(dst, backup_path)

        print("Бэкап", f"Бэкап сделан: {backup_path}")

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
    temp_dir = None
    backup_dir = "updatelocalhistory"
    try:
        print("Обновление", "Проверка обновлений...")

        current_version = get_current_version()
        print("Текущая версия", f"Текущая версия: {current_version}")

        latest_version, asset_url = get_latest_version_info(repo_url)
        print("Последняя версия", f"Последняя версия: {latest_version}")

        if version.parse(current_version) > version.parse(latest_version):
            QMessageBox.information(None, "Тестовая версия", "Вы находитесь в тестовой версии приложения.")
            return

        if current_version == latest_version:
            QMessageBox.information(None, "Обновление", "Приложение в актуальной версии.")
            return

        QMessageBox.information(None, "Обновление", "Скачивание последней версии...")

        temp_dir = "temp_update"
        os.makedirs(temp_dir, exist_ok=True)

        extracted_root = download_and_extract_tarball(asset_url, temp_dir)

        print(None, "Обновление", "Обновление файлов приложения...")

        for item in os.listdir(extracted_root):
            s = os.path.join(extracted_root, item)
            d = os.path.join(os.getcwd(), item)
            backup_and_replace(s, d, backup_dir)

        with open("version.json", "w") as f:
            json.dump({"version": latest_version}, f)

        QMessageBox.information(None, "Обновление", "Приложение успешно обновлено!")

    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Ошибка обновления: {e}")

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    GITHUB_REPO_URL = "https://api.github.com/repos/Revellison/IntegralApp"
    update_application(GITHUB_REPO_URL)
