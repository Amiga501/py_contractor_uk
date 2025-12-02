# -*- coding: utf-8 -*-
"""
Created on Mon Nov 24 19:32:33 2025

@author: brendan

"""
# %% Global imports
from panel.viewable import ServableMixin
from tornado.web import RequestHandler

import panel as pn
import httpx
import secrets
import hashlib
import base64
import urllib.parse

# %% py_contractor imports
from py_contractor.config.config import Config

from py_contractor.config.loggers import PrototypeTestLogger


# %% Module level config

LOGGER = PrototypeTestLogger().logger

pn.extension()

# -----------------------------------------------------------------------------
OAUTH_AUTHORISE_URL = "https://test-www.tax.service.gov.uk/oauth/authorize"
OAUTH_TOKEN_URL = "https://test-api.service.hmrc.gov.uk/oauth/token"
CLIENT_ID = Config.hrmc_sandbox_client_id
REDIRECT_URI = "http://localhost:5006"
SCOPE = "read:vat write:vat"  # example, depends on API

CLIENT_SECRET = "ebed6ff7-818c-4d47-8d22-db7544d58e16"

# -----------------------------------------------------------------------------


# %% Functions


# %% Classes

# -----------------------------------------------------------------------------
class Dashboard(pn.viewable.Viewer):
    """!
    Controlling the dashboard from a central instance

    """
    
    # -------------------------------------------------------------------------
    def __init__(self, *,
                 blah: str = "",
                 **params,
                 ):
        """!
        **Instantiate the class**

        """
        self.logger = LOGGER
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # These need to be imported from .env or similar - offload that to 
        # config and let it handle the real source
        self.client_secret = CLIENT_SECRET
        self.client_id = CLIENT_ID
        self.redirect_uri = REDIRECT_URI
        self.scope = SCOPE
        self.oauth_authorise_url = OAUTH_AUTHORISE_URL
        self.oauth_token_url = OAUTH_TOKEN_URL

        self.template = pn.template.MaterialTemplate(
            title='Py Contractor',
            header_background='#015347',
            # favicon=FAVICON,
            )
        
        self.access_token = None
        
        self.__create_dashboard()
        
    # -------------------------------------------------------------------------
    def __create_dashboard(self):
        """!
        **Create the dashboard**
        
        """
        self.status = pn.pane.Markdown("### Not logged in.")
        
        login_button = pn.widgets.Button(
            name="Login with OAuth", 
            button_type="primary",
            )
        login_button.on_click(self.start_oauth)
        
        self.layout = pn.Column(
            "## OAuth Login Example",
            login_button,
            self.status,
        )
        
        self.template.main.append(self.layout)
            
    # -------------------------------------------------------------------------
    def create_template(self):
        """!
        **Return the template for the Dashboard**

        All of this is actually done in the __create_dashboard() method
        
        """
        pn.state.onload(lambda: self.handle_redirect())
        
        #return self.template    
        return self.layout
    
    # -----------------------------------------------------------------------------
    def exchange_code_for_token(self) -> str:
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
    def generate_pkce(self):
        """!
        
        """
        verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(40)
            ).rstrip(b"=").decode()
        
        hashed = hashlib.sha256(verifier.encode()).digest()
        
        challenge = base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()
        
        return verifier, challenge
        
    # -------------------------------------------------------------------------
    def handle_redirect(self):
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
            token = self.exchange_code_for_token()
            self.access_token = token
            self.status.object = "### Authentication complete! ✅"
        except Exception as e:
            self.status.object = f"### Error exchanging code: {e}"
        
    # -------------------------------------------------------------------------
    def start_oauth(self, event):
        """!
        **Start the OAuth journey**
        
        """        
        self.access_token = None
        self.code_verifier, self.code_challenge = self.generate_pkce()
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
    
        url = f"{self.oauth_authorise_url}?{urllib.parse.urlencode(params)}"
        
        self.status.object = f"[Click here to authenticate]({url})"
        
    

# -----------------------------------------------------------------------------
def main_app() -> ServableMixin:
    """!
    **Main Viewer creation function**

    """        
    app_ = Dashboard()
    
    return app_.create_template()


# %% Main
if __name__ == "__main__":
    
    pn.serve(
        main_app,
        port=5006,
        threaded=True,
        )

else:
    main_app().servable()
    