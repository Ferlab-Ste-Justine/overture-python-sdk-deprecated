"""
Package to abstract away Keycloak API calls
"""

import logging
import requests

def _get_logger():
    return logging.getLogger(__name__)

# pylint: disable=R0903
class KeyCloakClient:
    """
    Class to abstract away client calls to keycloak.

    The constructor takes the following parameters:
    base_url: Uri if your keycloak which is prepended to each url (ex: https://keycloak)
    client_id: ID of your client in keycloak
    client_secret: Secret of your client in keycloak
    verify_certificate: Whether the tls certificate should be validated to ensure it was
    signed by a valid CA
    """
    login_url = '{base_url}/protocol/openid-connect/token'

    def __init__(
            self,
            base_url,
            client_id,
            client_secret,
            verify_certificate=True
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.verify_certificate = verify_certificate

    def login(self, username, password):
        """
        Login to keycloak with the given username and password
        The access token is returned if successful, else an assertion error is thrown
        """
        res = requests.post(
            self.login_url.format(base_url=self.base_url),
            data={
                'username': username,
                'password': password,
                'grant_type': 'password',
                'scope': 'profile',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            },
            verify=self.verify_certificate
        )
        logger = _get_logger()
        logger.debug('login status code: %s', res.status_code)
        logger.debug('login response: %s', res.content)
        assert res.status_code == 200
        return res.json()['access_token']
