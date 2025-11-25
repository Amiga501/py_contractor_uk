# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 22:10:47 2025

@author: brendan

This module is for accessing the HMRC MTD VAT API endpoints.

For documentation around these endpoints, see:
    https://developer.service.hmrc.gov.uk/api-documentation
        /docs/api/service/vat-api/1.0
    https://developer.service.hmrc.gov.uk/guides
        /vat-mtd-end-to-end-service-guide
        /#production-approvals-process-for-vat-mtd
    https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service
        /vat-api/1.0/oas/page#tag/organisations/operation
        /RetrieveVATobligations
        
"""
# %% Global modules
from collections.abc import Callable
from httpx_retries import Retry, RetryTransport

import httpx  

# %% py_contractor modules
from py_contractor.config.config import Config
from py_contractor.config.loggers import HmrcLogger

# %% Module level config


# %% Functions


# %% Classes

# -----------------------------------------------------------------------------
class HmrcVatApi:
    """!
    **For accessing the HMRC MTD VAT API**
    
    """
    
    # -------------------------------------------------------------------------
    def __init__(self, *, 
                 logger: Callable,
                 url: str,
                 vrn: int,
                 ):
        """!
        **Instantiate**
        
        @param [in] logger [Callable] A logger handle
        @param [in] url [str] The main url of the HMRC API - done this way to
            make testing easier
        @param [in] vrn [int] The Vat Registration Number
            
        """
        self.logger = logger
        self.main_url = url
        self.vrn = vrn
        
    # -------------------------------------------------------------------------
    def __run_query(self, 
                    query_type: str,
                    url: str,
                    params: dict,
                    ) -> dict:
        """!
        **Run a query**
        
        Incorporates backoff strategy
        
        """
        retry = Retry(total=5, backoff_factor=0.5)
        transport = RetryTransport(retry=retry)

        with httpx.Client(transport=transport) as client:
            caller = getattr(client, query_type)
            response = caller(url,
                              params=params)
        
        if not response.status_code == 200:
            return {"success": False,
                    "reason": response.text,  # Sh/Could I pack the json here?
                    "data": {}}
        return {"success": True,
                "reason": "success",
                "data": response.json()}
    
    # -------------------------------------------------------------------------
    def retrive_obligations(self, *, 
                            date_from: str = None,
                            date_to: str = None,
                            is_open_status: bool = True,
                            ) -> dict:
        """!
        **Retrieve VAT obligations**
        
        @param [in] date_from [str] In form 'YYYY-MM-DD', mandatory unless 
            is_open_status is False
        @param [in] date_to [str] In form 'YYYY-MM-DD', mandatory unless
            is_open_status is False
        @param [in] is_open_status [bool] If true, will send status 'O' to API
            otherwise will send 'F' (fulfilled) to API
            
        @return [dict]
        
        """
        url = f"{self.main_url}/organisations/vat/{self.vrn}/obligations"
        
        params = {}
        for k, v in {"from": date_from,
                     "to": date_to,
                     "status": {True: "O", False: "F"}.get(is_open_status),
                     }.items():
            if v is not None:
                params[k] = v
                
        return self.__run_query("get", 
                                url, 
                                params)
        