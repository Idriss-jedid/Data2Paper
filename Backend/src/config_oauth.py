"""
OAuth Configuration for Google, GitHub, and Apple authentication
"""
import os
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# Load environment variables
config = Config('.env')

# OAuth settings
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')

GITHUB_CLIENT_ID = config('GITHUB_CLIENT_ID', default='')
GITHUB_CLIENT_SECRET = config('GITHUB_CLIENT_SECRET', default='')

APPLE_CLIENT_ID = config('APPLE_CLIENT_ID', default='')
APPLE_CLIENT_SECRET = config('APPLE_CLIENT_SECRET', default='')
APPLE_TEAM_ID = config('APPLE_TEAM_ID', default='')
APPLE_KEY_ID = config('APPLE_KEY_ID', default='')

# OAuth client configuration
oauth = OAuth()

# Google OAuth configuration
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# GitHub OAuth configuration
oauth.register(
    name='github',
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Apple OAuth configuration (Sign in with Apple)
oauth.register(
    name='apple',
    client_id=APPLE_CLIENT_ID,
    client_secret=APPLE_CLIENT_SECRET,
    authorize_url='https://appleid.apple.com/auth/authorize',
    access_token_url='https://appleid.apple.com/auth/token',
    client_kwargs={
        'scope': 'name email',
        'response_mode': 'form_post'
    }
)

# OAuth provider metadata
OAUTH_PROVIDERS = {
    'google': {
        'name': 'Google',
        'icon': 'google',
        'color': '#4285f4',
        'scope': 'openid email profile'
    },
    'github': {
        'name': 'GitHub',
        'icon': 'github',
        'color': '#333',
        'scope': 'user:email'
    },
    'apple': {
        'name': 'Apple',
        'icon': 'apple',
        'color': '#000',
        'scope': 'name email'
    }
}
