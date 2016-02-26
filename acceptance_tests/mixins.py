import datetime
import logging

from edx_rest_api_client.client import EdxRestApiClient
import jwt

from acceptance_tests import config
from acceptance_tests.pages import LMSLoginPage


log = logging.getLogger(__name__)


class LoginMixin(object):
    """ Mixin used for log in through LMS login page."""

    def setUp(self):
        super(LoginMixin, self).setUp()
        self.lms_login_page = LMSLoginPage(self.browser)

    def login_with_lms(self):
        """ Visit LMS and login."""
        email = config.LMS_EMAIL
        password = config.LMS_PASSWORD

        self.lms_login_page.browser.get(self.lms_login_page.url())  # pylint: disable=not-callable
        self.lms_login_page.login(email, password)


class CredentialsApiMixin(object):
    """ Mixin used for login on credentials."""
    def setUp(self):
        super(CredentialsApiMixin, self).setUp()
        self.data = None

    @property
    def credential_api_client(self):
        now = datetime.datetime.utcnow()
        expires_in = 60
        payload = {
            "iss": config.OAUTH_URL,
            "aud": config.USER_JWT_AUDIENCE,
            "exp": now + datetime.timedelta(seconds=expires_in),
            "iat": now,
            "preferred_username": config.LMS_USERNAME,
            "administrator": True,
        }
        try:
            jwt_data = jwt.encode(payload, config.JWT_SECRET_KEY)
            api_client = EdxRestApiClient(config.CREDENTIALS_API_URL, jwt=jwt_data)
        except Exception:  # pylint: disable=broad-except
            log.exception("Failed to initialize the API client with url '%s'.", config.CREDENTIALS_API_URL)
            return
        return api_client

    def create_credential(self):
        """Create user credential for a program."""
        self.data = self.credential_api_client.user_credentials.post({
            'username': config.LMS_USERNAME,
            'credential': {'program_id': config.PROGRAM_ID},
            'attributes': []
        })

    def change_credential_status(self, status):
        """Update the credential status to awarded or revoked."""
        self.data['status'] = status
        self.credential_api_client.user_credentials(self.data['id']).patch(self.data)
