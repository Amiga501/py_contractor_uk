# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 10:31:05 2023

@author: brendans1020

"""
from collections.abc import Callable
from pathlib import Path

import logging.config
import structlog
import sys


# %% Module level configuration

'''
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H-%M-%S.%f", 
                                         utc=True),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False
)
'''


# -----------------------------------------------------------------------------
class Logger():
    """
    Wrapper around the logging class with a few more useful methods
    """

    # -------------------------------------------------------------------------
    def __init__(self, *,
                 logger_name: str = None,
                 log_file: str = None,
                 log_level: str = "DEBUG",
                 ):
        """!
        Start a new logger instance

        @param [in] logger_name [str] The name of the logger
        @param [in] log_file [str] The name of the log file, leave empty for 
            stream only
        @param [in] log_level [str] One of "DEBUG", "INFO", "WARNING", "ERROR"
        
        """
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
            }
        log_level_= log_levels.get(log_level) or logging.DEBUG
        
        timestamper = structlog.processors.TimeStamper(fmt="iso")
        
        dict_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "default": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                },
            }
        }
        handlers_ = ["default"]
        self.log_file_failure_msg = None
        if log_file:
            log_file = self.__create_log_file(log_file)
        
        if log_file:
            dict_config["handlers"]["file"] = {
                "level": "DEBUG",
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": log_file,
            }
            handlers_.append("file")
        
        dict_config["loggers"] = {
            "": {
                "handlers": handlers_,
                "level": "DEBUG",
                "propagate": True,
            },
        }
        
        logging.config.dictConfig(dict_config)
                
        structlog.configure(
            processors=[
                # Add callsite parameters.
                structlog.processors.CallsiteParameterAdder([
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    ],
                ),
                structlog.contextvars.merge_contextvars,
                structlog.dev.set_exc_info,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                timestamper,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            #wrapper_class=structlog.stdlib.BoundLogger,
            wrapper_class=structlog.make_filtering_bound_logger(log_level_),
            cache_logger_on_first_use=True,
        ) 

        # better to have too much log than not enough
        # May be changed later in get_logger()
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
            )
        self.logger = structlog.get_logger(logger_name)
        
        # with this pattern, it's rarely necessary to propagate the error up to
        # parent
        self.logger.propagate = False
        
        if self.log_file_failure_msg:
            self.logger.error(self.log_file_failure_msg)
            
    # -------------------------------------------------------------------------
    def __create_log_file(self, log_file: str) -> str:
        """!
        **Create a log file**
        
        @param [in] log_file [str] The proposed full file path of log file
        
        @return [str] the path of the actual log file, not necessarily the
            requested one!
        
        """
        if not Path(log_file).parent.is_dir():
            print("Invalid folder path specified for log file, will "
                  "attempt to create")
            if not Path(Path(log_file).drive).exists():
                self.log_file_failure_msg = (
                    "Unable to create log file at requested location, "
                    f"{log_file}, as drive doesn't exist', won't create log "
                    "file"
                    )
                log_file = None
            
            else:
                try:
                    Path(log_file).mkdir(parents=True, exist_ok=True)
                except Exception as exception:
                    self.log_file_failure_msg = (
                        "Unable to create log file at requested location, "
                        f"{log_file}, due to {exception}, won't create log"
                        )
                    log_file = None
                    
                try:
                    with open(log_file, "w") as f:
                        f.writelines(["\n"])
                        ...
                except Exception as exception:
                    self.log_file_failure_msg = (
                        "Unable to create log file at requested location, "
                        f"{log_file}, due to {exception}, won't create log"
                        )
                    log_file = None
                         
        return log_file
        
    # -------------------------------------------------------------------------
    def __get_console_handler(self) -> Callable:
        """
        From: https://www.toptal.com/python/in-depth-python-logging
        
        @return [Callable]
        
        """
        console_handler = logging.StreamHandler(sys.stdout)
        
        return console_handler

    # -------------------------------------------------------------------------
    def __get_file_handler(self, log_file: str):
        """
        From: https://www.toptal.com/python/in-depth-python-logging
        
        @param [in] log_file [str] Full file path to the intended log file
        
        @return [Callable]
        
        """
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file, 
            when='midnight')
        
        return file_handler

    # -------------------------------------------------------------------------
    def get_logger(self, *,
                   log_level: str = None,
                   ) -> Callable:
        """
        **Get handle to the logger instance**
        
        @param [in] log_level [str] Currently ignored
        
        """
        return self.logger

    # -------------------------------------------------------------------------
    def set_log_file(self, log_file: str):
        """
        Set the log file for the logger
        
        @param [in] log_file [str] Full file path to the intended log file
        
        """
        self.logger.addHandler(self.__get_file_handler(log_file))


# %% Main
if __name__ == "__main__":
    
    # Some cursory tests
    logger_ = Logger(logger_name="test",
                     log_file="test_1.log",
                     )

    logger = logger_.get_logger(log_level="INFO")
    
    logger.debug("Test debug")
    logger.info("Test info")
    logger.warning("Test warning")
    logger.error("Test error")
    logger.critical("Test critical")
