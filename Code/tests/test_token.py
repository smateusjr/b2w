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


class TestToken(AsyncHTTPTestCase):

    def get_app(self):
        self.config = CONFIG
        unused_sock, dummy.args.port = bind_unused_port()
        return restapi.main(dummy.args)

    def post_authorization_token(self):

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
        response_body = json.loads(response.body.decode('utf-8'))
        return response_body

    def get_authorization_token(self, token):
        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    token=token
                ),
                doseq=True
        )
        response = self.fetch(
            '/v1/planet/token/?%s' % params,
            method='GET'
        )
        return response


class TestTokenSuccess(TestToken):

    def test_success_get_token(self):
        authorization_token = self.post_authorization_token()
        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    token=authorization_token['access_token']
                ),
                doseq=True
        )
        response = self.fetch(
            '/v1/planet/token/?%s' % params,
            method='GET'
        )
        self.assertEqual(response.code, 200)

        response_body = json.loads(response.body.decode('utf-8'))
        self.assertTrue('access_token' in response_body.keys())

    def test_success_post_token_refresh_revoke_token(self):
        authorization_token = self.post_authorization_token()

        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    token=authorization_token['refresh_token'],
                    grant_type='refresh_token'
                )
        )
        # Refresh
        response = self.fetch(
            '/v1/planet/token/',
            method='POST',
            body=params
        )
        self.assertEqual(response.code, 200)

        response_body = json.loads(response.body.decode('utf-8'))
        self.assertTrue('access_token' in response_body.keys())

        # check remove old token
        get_token = self.get_authorization_token(
            authorization_token['access_token']
        )
        self.assertEqual(get_token.code, 401)

        response_body_get_token = json.loads(get_token.body.decode('utf-8'))
        self.assertTrue('error' in response_body_get_token.keys())
        self.assertEqual(response_body_get_token['error'], 'invalid_token')
        self.assertEqual(
            response_body_get_token['error_description'],
            'Token is Invalid.: Token is Invalid.'
        )

        # Revoke
        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    token=response_body['access_token'],
                    grant_type='revoke_token'
                )
        )
        response = self.fetch(
            '/v1/planet/token/',
            method='POST',
            body=params
        )
        self.assertEqual(response.code, 200)

        # check revoked token
        get_token = self.get_authorization_token(response_body['access_token'])
        self.assertEqual(get_token.code, 401)

        response_body_get_token = json.loads(get_token.body.decode('utf-8'))
        self.assertTrue('error' in response_body_get_token.keys())
        self.assertEqual(response_body_get_token['error'], 'invalid_token')
        self.assertEqual(
            response_body_get_token['error_description'],
            'Token is Invalid.: Token is Invalid.'
        )


class TestTokenFails(TestToken):

    def test_fail_get_token_invalid_token(self):
        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    token='xxx'
                ),
                doseq=True
        )
        response = self.fetch(
            '/v1/planet/token/?%s' % params,
            method='GET'
        )
        self.assertEqual(response.code, 401)

        response_body_get_token = json.loads(response.body.decode('utf-8'))
        self.assertTrue('error' in response_body_get_token.keys())
        self.assertEqual(response_body_get_token['error'], 'invalid_token')
        self.assertEqual(
            response_body_get_token['error_description'],
            'Token is Invalid.: Token is Invalid.'
        )

    def test_fail_post_token_invalid_type_token(self):
        authorization_token = self.post_authorization_token()

        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    token=authorization_token['access_token'],
                    grant_type='refresh_token'
                )
        )
        response = self.fetch(
            '/v1/planet/token/',
            method='POST',
            body=params
        )
        self.assertEqual(response.code, 401)

        response_body_get_token = json.loads(response.body.decode('utf-8'))
        self.assertTrue('error' in response_body_get_token.keys())
        self.assertEqual(response_body_get_token['error'], 'invalid_token')
        self.assertEqual(
            response_body_get_token['error_description'],
            'Token is Invalid.: Token is Invalid.'
        )
