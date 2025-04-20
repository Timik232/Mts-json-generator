import logging

import requests

from json_generator import configure_logging, generate


def test_json_generator():
    """
    Test function to check if the JSON generator works correctly.
    """
    session_id = "test_session_123"
    message = "Мне нужно сделать rest api для получения списка вакансий. "

    url = "http://localhost:8000/chat"

    payload = {"session_id": session_id, "message": message}

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            logging.info("Успешно получено:", response.json())
        else:
            logging.error(f"Ошибка: {response.status_code}")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


def main():
    msg = generate("Привет. Ты кто?")
    logging.info(msg)


if __name__ == "__main__":
    configure_logging(logging.DEBUG)
    # main()
    test_json_generator()
