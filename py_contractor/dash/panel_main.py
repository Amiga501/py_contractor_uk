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
from dotenv import load_dotenv

import base64
import hashlib
import httpx
import os
import panel as pn
import secrets
import urllib.parse


# %% py_contractor imports
from py_contractor.config.config import Config
from py_contractor.config.loggers import DashLogger


# %% Module level config

pn.extension("tabulator")

LOGGER = DashLogger().logger

if not load_dotenv(Config.ENV_FILE):
    LOGGER.critical("No configuration file found, dashboard will fail")

# %% Functions

def main_app():
    """!
    **Create the app**
    
    """
    app = PanelApp(
        logger=LOGGER,
        )
    
    return app.run()


# %% Classes

# -----------------------------------------------------------------------------
class PanelApp:    
    """!
    The dashboard
    
    """

    # -------------------------------------------------------------------------
    def __init__(self, *,
                 logger: Callable,
                 ):
        """!
        **Instantiate**
        
        """        
        self.logger = logger
        
        if not self.__get_env_vars():
            self.template = None
            return
        
        self.__create_template()
        
    # -------------------------------------------------------------------------
    def __continue_hmrc_oauth(self, event):
        """!        
        Continue the HMRC login journey
        
        """   
        breakpoint()
                
    # -------------------------------------------------------------------------
    def __create_sidebar(self):
        """!
        **Create the sidebar links**
        
        """
        
    # -------------------------------------------------------------------------
    def __create_template(self):
        """!
        **Create the template and add objects**
        
        """
        self.__create_template_authorisation()
        self.__create_template_vat_history()
        self.__create_template_vat_submission()
        
        self.tabs = pn.Tabs(
            ("Authorisation", self.layout_authorisation),
            ("VAT History", self.layout_vat_history),
            ("VAT Submission", self.layout_vat_submission),      
            )
        
        self.template = pn.template.FastListTemplate(
            title="py_contractor",
            theme="dark",
            header_background="green",
            )
        
        self.template.main.append(self.tabs)
        
    # -------------------------------------------------------------------------
    def __create_template_authorisation(self):
        """!
        **Create the authorisation template**
        
        Local authorisation and HMRC authorisation
        
        """
        self.app_login_status = pn.indicators.BooleanStatus(
            value=False,
            color="success",
            )
        self.hrmc_login_status = pn.indicators.BooleanStatus(
            value=False,
            color="success",
            )
        
        login_app_button = pn.widgets.Button(
            name="Login to App", 
            button_type="primary",
            )
        login_app_button.on_click(self.__start_app_auth)
        
        login_hmrc_button = pn.widgets.Button(
            name="Login to HMRC (OAuth)", 
            button_type="primary",
            )
        login_hmrc_button.on_click(self.__start_hmrc_oauth)
        
        self.login_hmrc_button2 = pn.widgets.Button(
            name="Authenticate with HMRC (OAuth)", 
            button_type="primary",
            disabled=True
            )
        #self.login_hmrc_button2.on_click(self.__continue_hmrc_oauth)
        
        self.layout_authorisation = pn.Column(
            login_app_button,
            login_hmrc_button,
            self.login_hmrc_button2,
            
            self.app_login_status,
            self.hrmc_login_status
        )
        
    # -------------------------------------------------------------------------
    def __create_template_vat_history(self):
        """!
        **VAT History**
        """
        self.layout_vat_history = pn.pane.Markdown(
            "VAT History goes here")
        
    # -------------------------------------------------------------------------
    def __create_template_vat_submission(self):
        """!
        **VAT Submission**
        """
        self.layout_vat_submission = pn.pane.Markdown(
            "VAT Submission goes here")
        
    # -----------------------------------------------------------------------------
    def __exchange_code_for_token(self) -> str:
        """!
        Exchange authorization code for access token.
        
        @param [in] code [str]
        @param [in] code_verifier [str]
        
        @return [str]
        
        """
        data = {
            "client_secret": self.client_secret,
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": self.code,
            "code_verifier": self.code_verifier,
        }
        with httpx.Client() as client:
            resp = client.post(self.oauth_token_url, data=data)
            resp.raise_for_status()
            return resp.json().get("access_token")
        
    # -------------------------------------------------------------------------
    def __generate_pkce(self) -> tuple:
        """!
        **Create the Proof Key for Code Exchange**
        
        @return [tuple]
        
        """
        verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(40)
            ).rstrip(b"=").decode()
        
        hashed = hashlib.sha256(verifier.encode()).digest()
        
        challenge = base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()
        
        return verifier, challenge
        
    # -------------------------------------------------------------------------
    def __get_env_vars(self) -> bool:
        """!
        **Pull env vars into the class**
        
        @return [bool] True if all necessary vars found, False otherwise
        
        """        
        vars_ = ["CLIENT_SECRET",
                 "CLIENT_ID",
                 "REDIRECT_URI",
                 "SCOPE",
                 "OAUTH_AUTHORISE_URL",
                 "OAUTH_TOKEN_URL"
                 ]
        
        for var_ in vars_:
            if not (val := os.environ.get(var_)):
                self.logger.error(
                    f"Required environmental var: {var_} not found, won't be "
                    "able to complete setup")
                return False
            setattr(self, var_.lower(), val)
        
        return True
    
    # -------------------------------------------------------------------------
    def __handle_auth_redirect(self):
        """!
        **Check browser URL for OAuth redirect parameters and exchange code.**
        
        """        
        search = pn.state.location.search
        if not search:
            return
        
        params = urllib.parse.parse_qs(search[1:])  # remove ?
        self.code = params.get("code", [None])[0]
        returned_state = params.get("state", [None])[0]

        # Retrieve state/code_verifier from hidden widgets
        expected_state = pn.state.cache["secrets_state"]
        self.code_verifier = pn.state.cache["secrets_verifier"]
                
        # Already handled or no code
        if not self.code or self.access_token:
            return

        if returned_state != expected_state:
            self.status.object = "### State mismatch — possible CSRF!"
            return

        try:
            token = self.__exchange_code_for_token()
            self.access_token = token
            self.status.object = "### Authentication complete! ✅"
        except Exception as e:
            self.status.object = f"### Error exchanging code: {e}"
            
    # -------------------------------------------------------------------------
    def __start_app_auth(self, event):
        """!
        **Start the APP Auth journey**
        
        """
        
            
    # -------------------------------------------------------------------------
    def __start_hmrc_oauth(self, event):
        """!
        **Start the HMRC OAuth journey**
        
        """        
        self.access_token = None
        self.code_verifier, self.code_challenge = self.__generate_pkce()
        self.state = secrets.token_urlsafe(16)
        
        pn.state.cache["secrets_state"] = self.state
        pn.state.cache["secrets_verifier"] = self.code_verifier
    
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": self.state,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }
        
        self.hmrc_oauth_url = ( 
            f"{self.oauth_authorise_url}?{urllib.parse.urlencode(params)}")
        
        self.login_hmrc_button2.js_on_click(
            args={"url": self.hmrc_oauth_url},
            code="window.open(url, '_blank')"
            )
        
        self.login_hmrc_button2.disabled = False
        
    # -------------------------------------------------------------------------
    def run(self):
        """!
        **Run the webapp**
        
        """        
        pn.state.onload(lambda: self.__handle_auth_redirect())
        
        return self.template
            
        
    
    
# %% Main
if __name__ == "__main__":
    
    pn.serve(
        main_app,
        port=5006,
        threaded=True,
        )

else:
    main_app().servable()
    
    