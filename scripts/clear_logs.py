"""
Clear Logs Script
"""

from pathlib import Path

from defs import LOG_DIR_PATH


def clear_logs() -> bool:
    """
    Clears the logs directory
    """

    delete_success: bool = True

    # Get log files
    try:
        log_files = list(Path(LOG_DIR_PATH).glob('*.log'))
        print(f'Clearing {len(log_files)} log files...')
    except FileNotFoundError:
        return False

    # Iterate over log files
    for log_file in log_files:
        # Clear log file
        try:
            log_file.unlink()
            log_file.touch()
            print(f'Cleared log file: {log_file}.')

        # Error clearing log file
        except OSError as error:
            print(f'Error deleting log file: {log_file}. Error: {error}')
            delete_success = False

    return delete_success


if __name__ == '__main__':
    clear_logs()
