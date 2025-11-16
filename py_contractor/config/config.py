# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 20:52:50 2025

@author: Brendan

Configuration file for py_efficient_payer

Some stuff may be stored in .env file

"""
# %% Global imports
from pathlib import Path

import importlib.util
import os
import platform


# %% py_efficient_payer imports


# %% Module level config

host_drive_map = {
    "Barricade": "C:",
    "Megatron": "E:",
    }

library_dir = Path(importlib.util.find_spec(
    "py_efficient_payer").submodule_search_locations[0]).parent


# %% Functions

def is_running_in_github_actions() -> bool:
    """!
    **Determine if instance is running in GitHub CI/CD**
    
    @return [bool] True if in GitHub actions
    
    """
    # GitHub sets this variable to "true" in GitHub Actions
    return os.getenv("GITHUB_ACTIONS", "").lower() == "true"


# %% Classes

class Config:
    
    if not is_running_in_github_actions():
        log_drive = host_drive_map.get(platform.node()) or Path.cwd().drive
        # This reverts to the drive holding the file if its not in explicit map
        
    else:
        log_drive = os.getenv("GITHUB_WORKSPACE", os.getcwd())
                
    
    LOG_DIR = str(Path(f"{log_drive}\\", "Logs", "py_efficient_payer"))
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    
    TEST_SUPPORTING_DATA = str(Path(library_dir,
                                    "py_efficient_payer",
                                    "tests",
                                    "supporting_data"))
    
    TEST_REPORTS = str(Path(library_dir,
                            "py_efficient_payer",
                            "tests",
                            "reports"))

    
    basic_tax_lwr_thres = 12570
    higher_tax_lwr_thres = 50270
    super_tax_lwr_thres = 125140 
    
    basic_tax_rate_pc = 20
    higher_tax_rate_pc = 40 
    super_tax_rate_pc = 45
    
    