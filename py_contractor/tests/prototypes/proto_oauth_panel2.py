import panel as pn
import httpx
import secrets
import hashlib
import base64
import urllib.parse
from tornado.web import RequestHandler

pn.extension()

# ======================================================================
#   OAUTH CLIENT CLASS (Panel 1.8.3 compatible)
# ======================================================================

class OAuthClient:
    def __init__(self, authorize_url, token_url, client_id, redirect_uri, scope):
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope

        self.state = None
        self.code_verifier = None
        self.access_token = None

        self.status = pn.pane.Markdown("### Not logged in.")
        self.login_button = pn.widgets.Button(name="Login", button_type="primary")
        self.login_button.on_click(self.start_authorization)

    # ----------------------------
    # PKCE generation
    # ----------------------------
    def generate_pkce(self):
        verifier = base64.urlsafe_b64encode(secrets.token_bytes(40)).rstrip(b"=").decode()
        hashed = hashlib.sha256(verifier.encode()).digest()
        challenge = base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()
        return verifier, challenge

    # ----------------------------
    # Start OAuth flow
    # ----------------------------
    def start_authorization(self, event):
        self.code_verifier, code_challenge = self.generate_pkce()
        self.state = secrets.token_urlsafe(16)

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": self.state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        url = f"{self.authorize_url}?{urllib.parse.urlencode(params)}"
        self.status.object = f"[Click here to log in]({url})"

    # ----------------------------
    # Tornado callback handler
    # ----------------------------
    async def handle_callback(self, request_handler: RequestHandler):
        args = request_handler.request.arguments
        code = args.get("code", [None])[0]
        state = args.get("state", [None])[0]

        if isinstance(code, bytes):
            code = code.decode()
        if isinstance(state, bytes):
            state = state.decode()

        if state != self.state:
            request_handler.write("State mismatch")
            return

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": self.code_verifier,
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(self.token_url, data=data)
            token_response.raise_for_status()
            tokens = token_response.json()

        self.access_token = tokens.get("access_token")
        self.status.object = f"### Login successful!\n```\n{self.access_token}\n```"

        request_handler.write("<h3>You may close this tab.</h3>")

    # ----------------------------
    # Panel layout
    # ----------------------------
    def panel(self):
        return pn.Column(
            "# OAuth Example (Panel 1.8.3)",
            self.login_button,
            self.status,
        )


oauth = OAuthClient(
    authorize_url="https://example.com/oauth/authorize",
    token_url="https://example.com/oauth/token",
    client_id="YOUR_CLIENT_ID",
    redirect_uri="http://localhost:5006/oauth_callback",
    scope="openid email profile",
)

# ----------------------------
# Register Tornado route at serve-time
# ----------------------------

def on_server_loaded(server_context):
    # Here pn.state.app and pn.state.http_server exist
    app = pn.state.app
    app.add_handlers(
        r".*", [
            (r"/oauth_callback", 
             lambda: type(
                 "CallbackHandler",
                 (RequestHandler,),
                 {"get": lambda self: oauth.handle_callback(self)}
             )()
            )
        ]
    )

pn.state.on_server_loaded(on_server_loaded)

# ----------------------------
# Panel entrypoint
# ----------------------------
app = oauth.panel()

pn.serve(app)