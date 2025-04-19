import asyncio
import logging

from json_generator import autogen_test, configure_logging

if __name__ == "__main__":
    configure_logging(logging.DEBUG)
    # msg = generate("Привет. Ты кто?")

    # logging.info(msg)
    asyncio.run(autogen_test())
