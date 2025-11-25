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
OAUTH_AUTHORIZE_URL = "https://test-www.tax.service.gov.uk/oauth/authorize"
OAUTH_TOKEN_URL = "https://test-api.service.hmrc.gov.uk/oauth/token"
CLIENT_ID = Config.hrmc_sandbox_client_id
REDIRECT_URI = "http://localhost:5006"
SCOPE = "read:vat write:vat"  # example, depends on API

# -----------------------------------------------------------------------------
code_verifier = None
access_token = None


# %% Functions


# %% Classes

# -----------------------------------------------------------------------------
class Dashboard(pn.viewable.Viewer):
    """!
    Controlling the dashboard from a central instance

    """
    
    # -------------------------------------------------------------------------
    def __init__(self, *,
                 analyser: str = "Rabta",
                 **params,
                 ):
        """!
        **Instantiate the class**

        """
        self.logger = LOGGER

        self.template = pn.template.MaterialTemplate(
            title='Py Contractor',
            header_background='#015347',
            # favicon=FAVICON,
            )
        
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
        
        layout = pn.Column(
            "## OAuth Login Example",
            login_button,
            self.status,
        )
        
        self.template.main.append(layout)
            
    # -------------------------------------------------------------------------
    def create_template(self):
        """!
        **Return the template for the Dashboard**

        All of this is actually done in the __create_dashboard() method
        
        """
        
        return self.template
        
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
    
    # -----------------------------------------------------------------------------
    def handle_callback(self, request_handler: RequestHandler):
        """
        Panel automatically calls this when the user visits /oauth_callback.
        
        """
        global access_token
        
        args = request_handler.request.arguments
        authorization_code = args.get("code", [None])[0]
        returned_state = args.get("state", [None])[0]

        if isinstance(authorization_code, bytes):
            authorization_code = authorization_code.decode()
        if isinstance(returned_state, bytes):
            returned_state = returned_state.decode()
    
        if not authorization_code:
            return pn.pane.Markdown("### No authorization code received.")
    
        if returned_state != self.state:
            return pn.pane.Markdown("### State mismatch — possible CSRF detected!")
    
        # Exchange authorization code for tokens
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "code_verifier": code_verifier,
        }
    
        with httpx.Client() as client:
            token_response = client.post(OAUTH_TOKEN_URL, data=data)
            token_response.raise_for_status()
            token_data = token_response.json()
            access_token = token_data.get("access_token")
    
        LOGGER.info(
            f"### Logged in!\n\nAccess Token:\n```\n{access_token}\n```")
    
        return pn.pane.Markdown(
            "### Authentication complete! You may close this tab.")
        
    # -----------------------------------------------------------------------------
    def start_oauth(self, event):
        
        self.code_verifier, self.code_challenge = self.generate_pkce()
        self.state = secrets.token_urlsafe(16)
    
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPE,
            "state": self.state,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }
    
        url = f"{OAUTH_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
        
        self.status.object = f"[Click here to authenticate]({url})"
    

# -----------------------------------------------------------------------------
def main_app() -> ServableMixin:
    """!
    **Main Viewer creation function**

    """    
    
    app_ = Dashboard()
    
    dashboard = app_.create_template()
    
    return dashboard


# %% Script 

app_ = main_app()


# -------------------------------------------------------------------------
def install_oauth_route(event):
    app = pn.state.app
    if getattr(app, "_oauth_route_installed", False):
        return  # Prevent duplicate installs

    class OAuthCallback(RequestHandler):
        async def get(self):
            await app_.handle_callback(self)

    app.add_handlers(r".*", [(r"/oauth_callback", OAuthCallback)])
    app._oauth_route_installed = True
# -------------------------------------------------------------------------

pn.state.on_session_created(install_oauth_route)


# %% Main
if __name__ == "__main__":
    
    pn.serve({"py_contractor": main_app},
             port=5006,
             oauth_redirect_uri=REDIRECT_URI,
             # show=False,
             threaded=True,
             n_threads=4,
             # num_procs=4,  # Of course, on Windows limited to == 1
             # probably due to thread spawn
             )

else:
    main_app().servable()
    