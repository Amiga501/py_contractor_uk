# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 20:51:52 2025

@author: Brendan

"""
# %% Global imports
from pathlib import Path


# %% py_efficient_payer imports
from py_efficient_payer.config.config import Config

from py_efficient_payer.lib.logging_config import Logger



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
class TestLogger:
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
       
