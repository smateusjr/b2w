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


class Testplanet(AsyncHTTPTestCase):

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

    def get_planet(self, authorization_token, add_param):
        params = dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
        )
        params.update(add_param)
        return self.fetch(
            '/v1/planet/?%s' % parse.urlencode(params, doseq=True),
            method='GET',
            headers={'Authorization': authorization_token}
        )


class TestplanetSuccess(Testplanet):

    def test_success_post_insert_planets(self):
        authorization_token = self.post_authorization_token()

        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    name='tatooine',
                    climate='Climate Tatooine',
                    terrain='Terrain Tatooine',
                    qtd_films=5
                )
        )
        response = self.fetch(
            '/v1/planet/',
            method='POST',
            body=params,
            headers={'Authorization': authorization_token['access_token']}
        )
        self.assertEqual(response.code, 200)

    def test_success_get_get_planets(self):
        authorization_token = self.post_authorization_token()

        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    name='Tatooine'
                ),
                doseq=True
        )
        response = self.fetch(
            '/v1/planet/?%s' % params,
            method='GET',
            headers={'Authorization': authorization_token['access_token']}
        )
        self.assertEqual(response.code, 200)

        response_body = json.loads(response.body.decode('utf-8'))
        self.assertGreater(int(len(response_body)), 0)

    def test_success_delete_delete_planets(self):
        authorization_token = self.post_authorization_token()
        # Get planet
        get_planet = self.get_planet(
            authorization_token['access_token'],
            dict(name='tatooine')
        )

        self.assertEqual(get_planet.code, 200)
        get_planet = json.loads(get_planet.body.decode('utf-8'))

        for i in get_planet:
            id_planet = i
        params = parse.urlencode(
                dict(
                    client_id=self.config['CLIENT_ID'],
                    client_secret=self.config['CLIENT_SECRET'],
                    id_planet=id_planet
                )
        )
        response = self.fetch(
            '/v1/planet/?%s' % params,
            method='DELETE',
            headers={'Authorization': authorization_token['access_token']}
        )
        self.assertEqual(response.code, 200)
        # check delete planet
        check_planet = self.get_planet(
            authorization_token['access_token'],
            dict(id_planet=id_planet)
        )
        self.assertEqual(check_planet.code, 200)


class TestplanetFail(Testplanet):

    def test_fail_get_invalid_id(self):
        authorization_token = self.post_authorization_token()

        response = self.get_planet(
            authorization_token['access_token'],
            dict(id_planet='tatooine')
        )

        self.assertEqual(response.code, 401)

        response_body = json.loads(response.body.decode('utf-8'))
        self.assertTrue('error' in response_body.keys())
        self.assertEqual(response_body['error'], 'invalid_id')
        self.assertEqual(
            response_body['error_description'],
            'Planet Id is Invalid.: Planet Id is Invalid.'
        )
