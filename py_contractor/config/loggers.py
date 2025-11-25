# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 20:51:52 2025

@author: Brendan

"""
# %% Global imports
from pathlib import Path

import pytest  # For setting TestLogger to ignore state


# %% py_contractor imports
from py_contractor.config.config import Config

from py_contractor.lib.logging_config import Logger



# %% Module level configuration



# -----------------------------------------------------------------------------
class DashLogger:
    """!
    Logger for the dashboard
    
    """
    
    # -------------------------------------------------------------------------
    def __init__(self):
        """!
        **Instance the logger**
        
        Consumer can access via the class handle's "logger" attr
        
        """
        logger = Logger(
            logger_name="dashboard",
            log_file=str(Path(Config.LOG_DIR, 
                              "dashboard.log")),
            )
        self.logger = logger.get_logger()
        
        
# -----------------------------------------------------------------------------
class HmrcLogger:
    """!
    Logger for interactions with HMRC APIs
    
    """
    
    # -------------------------------------------------------------------------
    def __init__(self):
        """!
        **Instance the logger**
        
        Consumer can access via the class handle's "logger" attr
        
        """
        logger = Logger(
            logger_name="hmrc",
            log_file=str(Path(Config.LOG_DIR, 
                              "hmrc.log")),
            )
        self.logger = logger.get_logger()


# -----------------------------------------------------------------------------
class _TestLogger:
    """!
    Logger for tests
    
    """
    
    # -------------------------------------------------------------------------
    def __init__(self):
        """!
        **Instance the logger**
        
        Consumer can access via the class handle's "logger" attr
        
        """
        logger = Logger(
            logger_name="tests",
            log_file=str(Path(Config.LOG_DIR, 
                              "tests.log")),
            )
        self.logger = logger.get_logger()
       

# -----------------------------------------------------------------------------
class PrototypeTestLogger:
    """!
    Logger for tests
    
    """
    
    # -------------------------------------------------------------------------
    def __init__(self):
        """!
        **Instance the logger**
        
        Consumer can access via the class handle's "logger" attr
        
        """
        logger = Logger(
            logger_name="tests",
            log_file=str(Path(Config.LOG_DIR, 
                              "tests.log")),
            )
        self.logger = logger.get_logger()
       
