# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 21:19:09 2025

@author: Brendan

Informal tests for core.paye.py

"""
# %% Global imports
from pathlib import Path
from pytest_jsonreport.plugin import JSONReport

import inspect
import os
import pytest  # Also needs pytest-html installed

# %% py_efficient_payer imports
from py_efficient_payer.config.config import Config
from py_efficient_payer.config.loggers import TestLogger

from py_efficient_payer.tests.lib.test_misc import MiscTest


# %% Unit under test
from py_efficient_payer.core.paye import Paye

# %% Module level config

LOGGER = TestLogger().logger

# %% Functions


# %% Classes

# -----------------------------------------------------------------------------
class Test__Paye:
    """!
    Class for testing the Paye class in core.paye.py module
    
    """
    
    # -------------------------------------------------------------------------
    def test__instance_object(self=None):
        """!
        Testing creation of a Paye object
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        
        paye_calc = Paye(
            logger=LOGGER,
            )
        
        attrs = {
            "basic_tax_lwr_thres": Config.basic_tax_lwr_thres,
            "higher_tax_lwr_thres": Config.higher_tax_lwr_thres,
            "super_tax_lwr_thres": Config.super_tax_lwr_thres,            
            "basic_tax_rate_pc": Config.basic_tax_rate_pc,
            "higher_tax_rate_pc": Config.higher_tax_rate_pc,
            "super_tax_rate_pc": Config.super_tax_rate_pc,
            }
        
        for key, val in attrs.items():
            assert (
                getattr(paye_calc, key) == val
                ), (f"Unexpected value for {key}, expected: {val}, got: " 
                    f"{getattr(paye_calc, key)}")
        
        MiscTest.demark_test()
        
    # -------------------------------------------------------------------------
    def test__zero_wage(self=None):
        """!
        Testing paye calculations for zero wage
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        
        paye_calc = Paye(
            logger=LOGGER,
            )
        
        paye_calc.calculate_from_wage(
            annual_wage=0,
            )
        
        attrs = {
            "basic_tax_amount": 0,
            "higher_tax_amount": 0,
            "super_tax_amount": 0,
            }
        
        for key, val in attrs.items():
            assert (
                getattr(paye_calc, key) == val
                ), (f"Unexpected value for {key}, expected: {val}, got: " 
                    f"{getattr(paye_calc, key)}")
        
        MiscTest.demark_test()
        
    # -------------------------------------------------------------------------
    def test__max_living_allowance(self=None):
        """!
        Testing paye calculations for wage at max living allowance
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        
        paye_calc = Paye(
            logger=LOGGER,
            )
        
        paye_calc.calculate_from_wage(
            annual_wage=Config.basic_tax_lwr_thres,
            )
        
        attrs = {
            "basic_tax_amount": 0,
            "higher_tax_amount": 0,
            "super_tax_amount": 0,
            }
        
        for key, val in attrs.items():
            assert (
                getattr(paye_calc, key) == val
                ), (f"Unexpected value for {key}, expected: {val}, got: " 
                    f"{getattr(paye_calc, key)}")
        
        MiscTest.demark_test()
        
    # -------------------------------------------------------------------------
    def test__max_basic_rate(self=None):
        """!
        Testing paye calculations for wage at max basic rate
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        
        paye_calc = Paye(
            logger=LOGGER,
            )
        
        paye_calc.calculate_from_wage(
            annual_wage=Config.higher_tax_lwr_thres,
            )
        
        attrs = {
            "basic_tax_amount": (
                (Config.higher_tax_lwr_thres - Config.basic_tax_lwr_thres)
                * (Config.basic_tax_rate_pc / 100)),
            "higher_tax_amount": 0,
            "super_tax_amount": 0,
            }
        
        for key, val in attrs.items():
            assert (
                getattr(paye_calc, key) == val
                ), (f"Unexpected value for {key}, expected: {val}, got: " 
                    f"{getattr(paye_calc, key)}")
        
        MiscTest.demark_test()
        
    # -------------------------------------------------------------------------
    def test__max_higher_rate(self=None):
        """!
        Testing paye calculations for wage at max higher rate
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        
        paye_calc = Paye(
            logger=LOGGER,
            )
        
        paye_calc.calculate_from_wage(
            annual_wage=Config.super_tax_lwr_thres,
            )
        
        attrs = {
            "basic_tax_amount": (
                (Config.higher_tax_lwr_thres - Config.basic_tax_lwr_thres)
                * (Config.basic_tax_rate_pc / 100)),
            "higher_tax_amount": (
                (Config.super_tax_lwr_thres - Config.higher_tax_lwr_thres)
                * (Config.higher_tax_rate_pc / 100)),
            "super_tax_amount": 0,
            }
        
        for key, val in attrs.items():
            assert (
                getattr(paye_calc, key) == val
                ), (f"Unexpected value for {key}, expected: {val}, got: " 
                    f"{getattr(paye_calc, key)}")
        
        MiscTest.demark_test()
        
    # -------------------------------------------------------------------------
    def test__super_higher_rate(self=None):
        """!
        Testing paye calculations for wage in super tax
        
        (wage is double the super tax min)
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        
        paye_calc = Paye(
            logger=LOGGER,
            )
        
        paye_calc.calculate_from_wage(
            annual_wage=Config.super_tax_lwr_thres * 2,
            )
        
        attrs = {
            "basic_tax_amount": (
                (Config.higher_tax_lwr_thres - Config.basic_tax_lwr_thres)
                * (Config.basic_tax_rate_pc / 100)),
            "higher_tax_amount": (
                (Config.super_tax_lwr_thres - Config.higher_tax_lwr_thres)
                * (Config.higher_tax_rate_pc / 100)),
            "super_tax_amount": ( 
                Config.super_tax_lwr_thres * Config.super_tax_rate_pc / 100),
            }
        
        for key, val in attrs.items():
            assert (
                getattr(paye_calc, key) == val
                ), (f"Unexpected value for {key}, expected: {val}, got: " 
                    f"{getattr(paye_calc, key)}")
        
        MiscTest.demark_test()
        

# %% Main
if __name__ == "__main__":
    
    # Setup for pytest
    outFileName = os.path.basename(__file__)[:-3]  # Remove the .py from end
    outFullFile = str(Path(Config.TEST_REPORTS,
                           outFileName))
    
    outFile = open(outFileName + ".log", "w")
    
    currScript = os.path.basename(__file__)
    
    json_plugin = JSONReport()

    # -------------------------------------------------------------------------
    # ---- PyTest execution
    pytest.main([currScript, '--html', outFullFile + '_report.html',
                 '--json-report-file=none'],
                plugins=[json_plugin],
                )