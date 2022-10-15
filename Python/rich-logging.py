import logging
from rich.text import Text
from datetime import datetime
from rich.console import Console

# Init logging
logging.basicConfig(level=logging.DEBUG,
                    datefmt="%I:%M:%S",
                    format="[%(asctime)s] %(levelname)s: %(message)s",
                    filename="script.log",
                    filemode="a")


# Logging and rich console output handler
def logger(msg, level='info'):
    if level != 'debug':
        timestamp = datetime.now().strftime("%I:%M:%S")

        console = Console()
        console.print(f"[{timestamp}]", end=" ")
        console.print(f"{msg}", highlight=False)

    msg = Text().from_markup(msg)

    if level == 'debug':
        logging.debug(msg)
    elif level == 'warning':
        logging.warning(msg)
    elif level == 'error':
        logging.error(msg)
    else:
        logging.info(msg)


if __name__ == '__main__':
    logger("This is an info log")  # default level is info
    logger("And this is one's a debug", level='debug')
