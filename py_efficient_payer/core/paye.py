# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 20:27:11 2025

@author: Brendan

This module contains all to do with PAYE

"""
# %% Global imports
from collections.abc import Callable

# %% py_efficient_payer imports
from py_efficient_payer.config.config import Config

# %% Module level config


# %% Funcctions


# %% Classes

# -----------------------------------------------------------------------------
class Paye:
    """!
    Control of calculations for PAYE
    
    """
    
    # -------------------------------------------------------------------------
    def __init__(self, *, 
                 logger: Callable,
                 ):
        """!
        **Instantiate**
        
        @param [in] logger [Callable] handle to the logger instance
        
        """
        self.logger = logger
        
        self.pension_contribution = 0
        
        self.__populate_dependencies()
        
    # -------------------------------------------------------------------------
    def __calculate_basic_tax(self):
        """!
        **Calculate the basic tax**
        
        """
        if self.taxable_wage <= self.basic_tax_lwr_thres:
            self.basic_tax_amount = 0
            return
        
        if self.taxable_wage > self.higher_tax_lwr_thres:
            self.basic_tax_amount = ((
                self.higher_tax_lwr_thres - self.basic_tax_lwr_thres) 
                * self.basic_tax_rate_pc / 100)
            return
        
        self.basic_tax_amount = ((
            self.taxable_wage - self.basic_tax_lwr_thres) 
            * self.basic_tax_rate_pc / 100)
        
    # -------------------------------------------------------------------------
    def __calculate_higher_tax(self):
        """!
        **Calculate the higher tax**
        
        """
        if self.taxable_wage <= self.higher_tax_lwr_thres:
            self.higher_tax_amount = 0
            return
        
        if self.taxable_wage > self.super_tax_lwr_thres:
            self.higher_tax_amount = ((
                self.super_tax_lwr_thres - self.higher_tax_lwr_thres) 
                * self.higher_tax_rate_pc / 100)
            return 
        
        self.higher_tax_amount = ((
            self.taxable_wage - self.higher_tax_lwr_thres) 
            * self.higher_tax_rate_pc / 100)
        
    # -------------------------------------------------------------------------
    def __calculate_super_tax(self):
        """!
        **Calculate the super tax**
        
        """
        if self.taxable_wage <= self.super_tax_lwr_thres:
            self.super_tax_amount = 0
            return
        
        self.super_tax_amount = ((
            self.taxable_wage - self.super_tax_lwr_thres) 
            * self.super_tax_rate_pc / 100)
        
    # -------------------------------------------------------------------------
    def __calculate_taxable_wage(self):
        """!
        **Determine the taxable wage**
        
        """
        self.taxable_wage = self.annual_wage - (
            self.pension_contribution)
        
        if self.taxable_wage < 0:
            self.logger.info(
                f"The taxable wage is <0 (actually: {self.taxable_wage}, this "
                "may be due to various reliefs etc and isn't necessarily " 
                "invalid - a refund from HMRC for previous years may be "
                "something to consider pursing")
            self.taxable_wage = 0
        
    # -------------------------------------------------------------------------
    def __populate_dependencies(self):
        """!
        **Get dependent values**
        
        Eventually will be populated via panel app, but for now, get from 
        config
        
        """        
        self.basic_tax_lwr_thres = Config.basic_tax_lwr_thres
        self.higher_tax_lwr_thres = Config.higher_tax_lwr_thres
        self.super_tax_lwr_thres = Config.super_tax_lwr_thres
        
        self.basic_tax_rate_pc = Config.basic_tax_rate_pc
        self.higher_tax_rate_pc = Config.higher_tax_rate_pc
        self.super_tax_rate_pc = Config.super_tax_rate_pc
        
    # -------------------------------------------------------------------------
    def calculate_from_wage(self, *, 
                            annual_wage: float,
                            pension_contribution: float = None,
                            ):
        """!
        **Calculate PAYE breakdown from wage**
        
        @param [in] annual_wage [float]
        @param [in] pension_contribution [float] Optional definition or 
            adjustment to pension contribution
        
        """
        self.annual_wage = annual_wage
        if pension_contribution:                
            self.pension_contribution = pension_contribution
        
        self.__calculate_taxable_wage()
        
        self.__calculate_basic_tax()
        self.__calculate_higher_tax()
        self.__calculate_super_tax()
        
        