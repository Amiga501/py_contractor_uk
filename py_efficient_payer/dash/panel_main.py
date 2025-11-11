# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 21:52:33 2025

@author: Brendan

The main panel app

Basic plan is to have 3x panels for initial MVP:
    - Summary comparison page of PAYE vs contractor
    - PAYE specific page
    - Contractor specific page

"""
# %% Global imports
from collections.abc import Callable

import panel as pn


# %% py_efficient_payer imports
from py_efficient_payer.config.loggers import DashLogger


# %% Module level config

pn.extension("tabulator")

LOGGER = DashLogger().logger


# %% Functions

def create_app():
    """!
    **Create the app**
    
    """
    app = PanelApp(
        logger=LOGGER,
        )
    
    return app


# %% Classes

# -----------------------------------------------------------------------------
class PanelApp:    
    """!
    The dashboard
    
    """

    # -------------------------------------------------------------------------
    def __init__(self, *
                 logger: Callable,
                 ):
        """!
        **Instantiate**
        
        """        
        self.logger = logger
        
        self.__create_template()
        
    # -------------------------------------------------------------------------
    def __create_template(self):
        """!
        **Create the template and add objects**
        
        """
        
        self.tabs = pn.Tabs()
        
        self.__create_template_summary()
        
        self.template = pn.template.FastGridTemplate(
            site="Panel", 
            title="py_efficient_payer", 
            prevent_collision=True,
            )
        
        self.template.main = self.tabs
        
    # -------------------------------------------------------------------------
    def __create_template_summary(self):
        """!
        **Create the summary tab objects**
        
        """
        layout1 = pn.Column(
            styles={"background": "green"}, 
            sizing_mode="stretch_both",
            )
        layout2 = pn.Column(
            styles={"background": "red"}, 
            sizing_mode="stretch_both",
            )
        layout3 = pn.Column(
            styles={"background": "blue"}, 
            sizing_mode="stretch_both",
            )
        
        self.tabs.append(
            pn.Column(
                pn.Row(layout1, layout2),
                layout3,
                )
            )
        
    # -------------------------------------------------------------------------