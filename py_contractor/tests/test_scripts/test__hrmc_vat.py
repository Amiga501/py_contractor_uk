# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 22:57:38 2025

@author: brendan

For testing the HMRC VAT MTD API accessor

"""
# %% Global imports
from httpx_retries import Retry, RetryTransport
from pathlib import Path
from pytest_jsonreport.plugin import JSONReport

import cachetools.func
import httpx
import inspect
import os
import pytest  # Also needs pytest-html installed


# %% py_contractor imports
from py_contractor.config.config import Config
from py_contractor.config.loggers import _TestLogger

from py_contractor.tests.lib.misc_test import MiscTest

# %% Unit under test
from py_contractor.core.hmrc_tax_api_accessor import HmrcVatApi

# %% Module level config

LOGGER = _TestLogger().logger

retry = Retry(total=5, backoff_factor=0.5)
transport = RetryTransport(retry=retry)

# %% Functions

@pytest.fixture(scope="session")
def create_test_user():
    """!
    Create a dummy user account for authentication
    
    Many of the HMRC APIs understandably require an authenticated user to 
    operate - this function creates a dummy
    
    """
    url = "https://test-api.service.hmrc.gov.uk/create-test-user/individuals"
    token = get_access_token()
    
    params = {
        "serviceNames": [
            # "national-insurance",
            # "self-assessment",
            # "mtd-income-tax",
            # "customs-services",
            # "goods-vehicle-movements",
            # "import-control-system",
            "mtd-vat",
            # "common-transit-convention-traders",
            # "common-transit-convention-traders-legacy",
            ],
        "eoriNumber": "123456789",  # Between 3 and 17 chars
        # Economic Operator Registration and Identification (EORI) number
        "nino": "987654321",  
        # National insurance number; only used with 'national-insurance'
        # and 'mtd-income-tax' services
        }

    with httpx.Client(transport=transport) as client:
        response = client.post(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            )
    
    rtn = response.json()
    breakpoint()

# -----------------------------------------------------------------------------
@cachetools.func.ttl_cache(maxsize=128, ttl=12600)  # TTL in secs, 3.5 hrs
def get_access_token() -> str:
    """!
    Use the client and secret to get an access token
    
    @return [str] The access token for use in subsequent queries
    
    """
    url = "https://test-www.tax.service.gov.uk/oauth/authorize"
    
    with httpx.Client(transport=transport) as client:
        response = client.get(
            url,
            params={
                "clientId": Config.hrmc_sandbox_client_id,
                },
            )
        response.raise_for_status()
    breakpoint()
    return response.json()["access_token"]
    

# %% Classes

# -----------------------------------------------------------------------------
class Test__VatSimple:
    """!
    Class for testing the HmrcVatApi class - simple scenario
    
    """
    
    # -------------------------------------------------------------------------
    def test__instance_object(self):
        """!
        Testing creation of instance of HmrcVatApi object
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        url = "https://test-api.service.hmrc.gov.uk",
        vrn = 123456789
        vat_api = HmrcVatApi(
            logger=LOGGER,
            url=url,
            vrn=vrn,
            )
        
        assert vat_api.main_url == url, (
            f"Expected instance url of {url}, but found {vat_api.main_url}")
        
        assert vat_api.vrn == vrn, (
            f"Expected instance vrn of {vrn}, but found {vat_api.vrn}")
        
        MiscTest.demark_test()
        
    # -------------------------------------------------------------------------
    def test__no_credentials(self):
        """!
        Testing request with no credentials supplied
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        url = "https://test-api.service.hmrc.gov.uk"
        vrn = 123456789
        vat_api = HmrcVatApi(
            logger=LOGGER,
            url=url,
            vrn=vrn,
            )
        
        rtn = vat_api.retrive_obligations()
        # Using the defaults
        
        assert rtn["success"] == False, (
            "Unexpected return for 'success', expected 'False', found: 'True'")
        
        assert rtn["data"] == {}, (
            "Unexpected return for 'data', expected '{}', found: "
            f"{rtn['data']}"
            )
        
        expected_reason = ('{"code": "MISSING_CREDENTIALS", "message": '
                           '"Authentication information is not provided"}')
        assert rtn["reason"] == expected_reason, (
            f"Unexpected return for 'reason', expected: {expected_reason}, "
            f"found: {rtn['reason']}")
        
        MiscTest.demark_test()
        
# -----------------------------------------------------------------------------
class Test__VatGetObligations:
    """!
    Class for testing the HmrcVatApi class - getting obligations
    
    """
    
    # -------------------------------------------------------------------------
    def test__nominal_open(self, create_test_user):
        """!
        Testing nominal obligations request
        
        """
        test = inspect.stack()[0][3]  # The name of this function (test)
        print(f"{test}()")
        
        url = "https://test-api.service.hmrc.gov.uk"
        vrn = 123456789
        vat_api = HmrcVatApi(
            logger=LOGGER,
            url=url,
            vrn=vrn,
            )
        
        rtn = vat_api.retrive_obligations()
        # Using the defaults
        
        breakpoint()
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
