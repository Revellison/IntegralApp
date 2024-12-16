import os
import shutil

def restore_backup(backup_dir="updatelocalhistory", restore_to=os.getcwd()):
    """Восстанавливает предыдущую версию из директории бэкапов."""
    try:
        # Проверяем, существует ли папка с бэкапами
        if not os.path.exists(backup_dir):
            print(f"Папка с бэкапами '{backup_dir}' не найдена.")
            return

        print(f"Восстановление из бэкапа '{backup_dir}'...")

        # Проходим по всем элементам в папке бэкапов
        for item in os.listdir(backup_dir):
            backup_item_path = os.path.join(backup_dir, item)
            restore_item_path = os.path.join(restore_to, item)

            # Если целевой элемент уже существует, удаляем его перед восстановлением
            if os.path.exists(restore_item_path):
                if os.path.isdir(restore_item_path):
                    shutil.rmtree(restore_item_path)
                else:
                    os.remove(restore_item_path)

            # Восстанавливаем элемент из бэкапа
            if os.path.isdir(backup_item_path):
                shutil.copytree(backup_item_path, restore_item_path)
            else:
                shutil.copy2(backup_item_path, restore_item_path)

            print(f"Восстановлено: {restore_item_path}")

        print("Восстановление завершено успешно.")

    except Exception as e:
        print(f"Ошибка при восстановлении: {e}")

if __name__ == "__main__":
    # Вызываем функцию восстановления
    restore_backup()
