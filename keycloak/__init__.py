import requests
import logging

logger = logging.getLogger(__name__)

class KeyCloakClient(object):
    login_url = '{base_url}/protocol/openid-connect/token'

    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
    
    def login(self, username, password):
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
            verify=False
        )
        logger.debug('login status code: {code}'.format(code=res.status_code))
        logger.debug('login response: {response}'.format(response=res.content))
        assert res.status_code == 200
        return res.json()['access_token']
