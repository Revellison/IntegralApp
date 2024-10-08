import requests
import time

# Токен API от Hugging Face
API_TOKEN = "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"  # Замените на ваш токен

# Заголовки для авторизации
headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# Запросить у пользователя ввод промта
user_input = input("Введите ваш промт: ")

# Тело запроса с вашим текстом (промптом)
data = {
    "inputs": user_input,
    "parameters": {
        "max_length": 500,
        "top_k": 50,
        "top_p": 0.95,
        "temperature": 1.0,
        "do_sample": True
    }
}

# Отправка POST-запроса с обработкой ошибок
for attempt in range(5):  # Максимум 5 попыток
    response = requests.post(
        "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B",  # Используем GPT-Neo
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
        print("Ошибка соединения: сервера модели перегружены. Повторная попытка через 5 секунд...")
        time.sleep(5)  # Ждем 30 секунд перед следующей попыткой
    else:
        print(f"Ошибка запроса: {response.status_code}")
        print("Ответ:", response.text)
        break  # Выходим из цикла при других ошибках
