# Ratelimit decorator for functions and methods

import logging
from tracker.utils import Logger
from time import time, sleep


class RateLimit:
    """
    Decorator for Rate-Limiting functions.
    Implements rolling window rate limiting.
    """

    def __init__(self,
                 limit: int | None = None,
                 period: int = 1,
                 max_wait: int | None = 10,
                 logger: logging.Logger | None = None):
        """ 
        RateLimit decorator for functions and methods

        :param limit: Number of times the function can be called
        :param period: Time in seconds between calls
        :param max_wait: Maximum time in seconds to wait before raising RateLimitException
        """

        # Initialize RateLimit
        self.limit: int | None = limit
        self.period: int = period
        self.max_wait: int | None = max_wait

        if logger is not None:
            self.logger: logging.Logger = logger
        else:
            self.logger = Logger('ratelimit', file_handler=True, stream_handler=True).get_logger()

        # Rate
        self.rate: float = limit / period

        # Initialize call time array to hold the last n (limit) calls
        self.call_times: list = [0] * (limit or 1)

        # Points to the first element in the call_times array
        self.call_times_index: int = 0

        # Initialize waiting variable to hold number of function calls waiting to be made
        self.waiting: int = 0

    def __call__(self, func: callable) -> callable:
        """
        Decorator for functions and methods

        :param func: Function to be decorated
        :return: Decorated function
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper function for RateLimit decorator.

            :param args: Arguments for the function
            :param kwargs: Keyword arguments for the function
            :return: Result of the function
            """

            # Get the current time in seconds
            now = time()

            # Calculate next permissible call time
            delta_time = self.call_times[self.call_times_index] + self.period

            # Check if the first call was made within the last period
            if delta_time >= now:
                # Calculate wait time
                wait_time = (delta_time - now) + (self.rate * (self.waiting % self.limit))

                # Log
                self.logger.info(f'RateLimit: Waiting {wait_time:.2f}s before calling '
                                 f'{func.__qualname__} from {func.__module__}. '
                                 f'args: {list(args)}. kwargs: {kwargs}.')

                # Check if wait time is greater than max_wait
                if self.max_wait is not None and wait_time > self.max_wait:
                    error_msg = f'Rate limit exceeded. Wait time: {wait_time}'
                    raise RateLimitException(error_msg, logger=self.logger)

                # Increment waiting and sleep
                self.waiting += 1
                sleep(wait_time)

            # Update the call time array
            self.call_times[self.call_times_index] = now

            # Increment the call time index
            self.call_times_index = (self.call_times_index + 1) % self.limit

            return func(*args, **kwargs)
        return wrapper


class RateLimitException(Exception):
    """
    Exception for Rate-Limiting
    """

    def __init__(self, message: str, logger: logging.Logger = None):
        """
        RateLimitException Constructor

        :param message: Exception Message
        :param logger: Logger
        """

        # Params
        self.message: str = message
        self.logger: logging.Logger | None = logger

        # Log the exception
        self.logger.exception(self.message)

        # Call the Exception constructor
        super().__init__(message)
