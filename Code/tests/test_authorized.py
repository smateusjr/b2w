from tornado.testing import AsyncHTTPTestCase
from tornado.testing import bind_unused_port
import os
import sys
import configobj
import json
from urllib import parse
import services.dummy_tests as dummy

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(APP_ROOT))
import main as restapi


if os.path.isfile('%s/configs/config_unit_test.ini' % APP_ROOT):
    CONFIG = configobj.ConfigObj('%s/configs/config_unit_test.ini' % APP_ROOT)
else:
    print('File config_unit_test.ini not found.')
    sys.exit(1)


class TestAuthorization(AsyncHTTPTestCase):

    def get_app(self):
        self.config = CONFIG
        sock, dummy.args.port = bind_unused_port()
        return restapi.main(dummy.args)


class TestTokenSuccess(TestAuthorization):

    def test_success_authorization_token(self):

        response = self.fetch(
            '/v1/planet/authorization/',
            method='POST',
            body=parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    login=self.config['USER'],
                    password=self.config['PASSWORD']
                )
            )
        )
        self.assertEqual(response.code, 200)

        response_body = json.loads(response.body.decode('utf-8'))
        self.assertTrue('access_token' in response_body.keys())


class TestAuthorizedFails(TestAuthorization):

    def test_fail_unauthorized_user(self):

        response = self.fetch(
            '/v1/planet/authorization/',
            method='POST',
            body=parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    login='xxx',
                    password='zzz'
                )
            )
        )
        self.assertEqual(response.code, 401)

        response_body = json.loads(response.body.decode('utf-8'))
        self.assertTrue('error' in response_body.keys())
        self.assertEqual(response_body['error'], 'unauthorized_user')
        self.assertEqual(
            response_body['error_description'], 'Unauthorized user.: Unauthorized user.'
        )
