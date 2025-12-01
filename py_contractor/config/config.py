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


# %% py_contractor imports


# %% Module level config

host_drive_map = {
    "Barricade": "C:",
    "Megatron": "E:",
    }

library_dir = Path(importlib.util.find_spec(
    "py_contractor").submodule_search_locations[0]).parent


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
        hard_drive = host_drive_map.get(platform.node()) or Path.cwd().drive
        # This reverts to the drive holding the file if its not in explicit map
        
    else:
        hard_drive = os.getenv("GITHUB_WORKSPACE", os.getcwd())
        
    ENV_DIR = str(Path(hard_drive, "config_files", "py_contractor_uk", ".env"))
                    
    LOG_DIR = str(Path(f"{hard_drive}\\", "Logs", "py_contractor"))
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    
    TEST_SUPPORTING_DATA = str(Path(library_dir,
                                    "py_contractor",
                                    "tests",
                                    "supporting_data"))
    
    TEST_REPORTS = str(Path(library_dir,
                            "py_contractor",
                            "tests",
                            "reports"))

    
    basic_tax_lwr_thres = 12570
    higher_tax_lwr_thres = 50270
    super_tax_lwr_thres = 125140 
    
    basic_tax_rate_pc = 20
    higher_tax_rate_pc = 40 
    super_tax_rate_pc = 45
    
    hmrc_vat_url = "https://test-api.service.hmrc.gov.uk"
    
    hrmc_sandbox_client_id = "ky9lbF19hDyEkNh2O89ygoRW72Pk"
    hmrc_sandbox_client_secret = "6f2df3ac-5daa-4637-8119-1fe9b5c61426"
    
    