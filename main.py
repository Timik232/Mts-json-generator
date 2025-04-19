import logging

from json_generator import configure_logging, generate

if __name__ == "__main__":
    configure_logging(logging.DEBUG)
    msg = generate("Привет. Ты кто?")
    logging.info(msg)
