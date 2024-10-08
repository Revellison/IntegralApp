import requests
import time

# Токен API от Hugging Face
API_TOKEN = "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"  # Замените на ваш токен

# Заголовки для авторизации
headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# Запросить у пользователя ввод промта
user_input = input("Введите ваш промт (например, 'Пожалуйста, ответьте на русском языке: '): ")

# Тело запроса с вашим текстом (промптом)
data = {
    "inputs": user_input,
    "parameters": {
        "max_length": 150,  # Увеличьте максимальную длину текста
        "top_k": 50,       # Установите топ K
        "top_p": 0.9,      # Измените значение top_p для большей предсказуемости
        "temperature": 0.7, # Уменьшите температуру для более связного текста
        "do_sample": True
    }
}

# Отправка POST-запроса с обработкой ошибок
for attempt in range(5):  # Максимум 5 попыток
    response = requests.post(
        "https://api-inference.huggingface.co/models/EleutherAI/gpt-neox-20b",  # Используем GPT-Neo
        headers=headers,
        json=data
    )

    # Проверка на успешность запроса
    if response.status_code == 200:
        response_data = response.json()
        print("Полный ответ от сервера:", response_data)

        if isinstance(response_data, list) and len(response_data) > 0 and "generated_text" in response_data[0]:
            generated_text = response_data[0]["generated_text"]
            print("Сгенерированный текст:", generated_text)
        else:
            print("Ошибка: В ответе нет сгенерированного текста.")
        break  # Успешный запрос, выходим из цикла
    elif response.status_code == 503:
        print("Ошибка 503: Модель загружается. Повторная попытка через 30 секунд...")
        time.sleep(30)  # Ждем 30 секунд перед следующей попыткой
    else:
        print(f"Ошибка запроса: {response.status_code}")
        print("Ответ:", response.text)
        break  # Выходим из цикла при других ошибках
