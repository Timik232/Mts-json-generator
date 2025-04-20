import logging

import requests

from json_generator import ClarifierSchema, configure_logging, generate


def test_json_generator():
    """
    Test function to check if the JSON generator works correctly.
    """
    session_id = "test_session_123"
    # message = "Мне нужно написать запрос через rest api"
    # message = ("мне надо схему, я принимаю запрос из верховного суда,"
    #            "нас всех судят нужно энтити в бд и на петровке,хакатон ,"
    #            "уголовная статья, sessionId=iolg4t0a")
    message = "type=TEXT, content=Прими из апи сообщение sessionId=cyjqiay3"
    url = "http://localhost:8000/chat"

    payload = {"session_id": session_id, "message": message}

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            logging.info(f"Успешно получено: {response.json()}")
        else:
            logging.error(f"Ошибка: {response.status_code}")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


def main():
    print(ClarifierSchema.model_json_schema())
    msg = generate("Привет. Ты кто?", json_schema=ClarifierSchema.model_json_schema())
    logging.info(msg)


if __name__ == "__main__":
    configure_logging(logging.DEBUG)
    # main()
    test_json_generator()
