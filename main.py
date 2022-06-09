# Main file

import sys

from streamlit import cli as stcli

from tracker.utils import Logger

# Define logger
main_logger = Logger('main')
logger = main_logger.get_logger()


def main() -> None:
    """
    Main Function
    """

    logger.info('Starting Streamlit App...')
    sys.argv = ["streamlit", "run", "streamlit_app.py"]

    try:
        sys.exit(stcli.main())

    except SystemExit(0):
        logger.info('Terminating Streamlit App...')

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
