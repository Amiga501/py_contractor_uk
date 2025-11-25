# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 20:19:49 2025

@author: brendan

"""
# %% Global modules
import httpx
import hashlib
import base64
import os
import secrets
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser

# %% py_contractor_uk modules
from py_contractor.config.config import Config


# %% Module level config

CLIENT_ID = Config.hrmc_sandbox_client_id
SCOPE = "read:vat write:vat"  # example, depends on API
#REDIRECT_URI = "http://localhost:8000"
REDIRECT_URI = "https://www.example.com/auth-redirect"
STATE = secrets.token_urlsafe(16)  # random string for CSRF protection


# -----------------------------------------------------------------------------
def generate_pkce_pair():
    # Random 43-128 character string for code_verifier
    code_verifier = base64.urlsafe_b64encode(os.urandom(64)).rstrip(b'=').decode()
    # SHA256 hash + base64-url encode for code_challenge
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return code_verifier, code_challenge


# -----------------------------------------------------------------------------
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        self.server.auth_code = params.get("code", [None])[0]
        self.server.state_received = params.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>You can close this window now.</h1></body></html>")

# -----------------------------------------------------------------------------
# Start HTTP server in background


# %% Main
if __name__ == "__main__":
    
    code_verifier, code_challenge = generate_pkce_pair()
    
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": STATE,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    
    AUTH_URL = (
        "https://test-www.tax.service.gov.uk/oauth/authorize?"
        f"{urllib.parse.urlencode(params)}")

    httpd = HTTPServer(("localhost", 8000), OAuthCallbackHandler)
    print("Opening browser for authorization...")
    webbrowser.open(AUTH_URL)
    
    # Wait for one request (the redirect)
    httpd.handle_request()
    auth_code = httpd.auth_code
    state_received = httpd.state_received
    
    if state_received != STATE:
        raise Exception("State mismatch! Possible CSRF attack.")
    
    print("Authorization code received:", auth_code)
    
    # ==========================
    # Step 4: Exchange code for access token
    # ==========================
    TOKEN_URL = "https://test-www.tax.service.gov.uk/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": code_verifier,
    }
    
    with httpx.Client() as client:
        response = client.post(TOKEN_URL, data=data)
        response.raise_for_status()
        token_data = response.json()


    print("Access token:", token_data.get("access_token"))
    print("Refresh token:", token_data.get("refresh_token"))
