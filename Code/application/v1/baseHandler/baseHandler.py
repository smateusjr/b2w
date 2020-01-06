import json

# Tornado
import tornado.ioloop
import tornado.web
import tornado.httputil
import tornado.escape

import services.token as token


class BaseHandler(tornado.web.RequestHandler):

    @property
    def config(self):
        instance = tornado.ioloop.IOLoop.instance()
        if hasattr(instance, 'config'):
            return instance.config
        else:
            return self.application.settings['config']

    @property
    def server_config(self):
        instance = tornado.ioloop.IOLoop.instance()
        if hasattr(instance, 'server_config'):
            return instance.server_config
        else:
            return self.application.settings['server_config']

    @property
    def redis_db_token(self):
        instance = tornado.ioloop.IOLoop.instance()
        if hasattr(instance, 'redis_db_token'):
            return instance.redis_db_token
        else:
            return self.application.settings['redis_db_token']

    @property
    def redis_db_swapi(self):
        instance = tornado.ioloop.IOLoop.instance()
        if hasattr(instance, 'redis_db_swapi'):
            return instance.redis_db_swapi
        else:
            return self.application.settings['redis_db_swapi']

    def initialize(self):
        self.utils = self.application.settings.get('utils')
        self.http_codes = self.config['http_codes']
        self.headers = self.utils.get_headers(self.request.headers)

        self.request.log = self.application.settings.get('logs')
        self.request.log.set_body(self.headers, self.request)

        self.request.log._info('Headers request', {'headers': self.headers})

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE')
        self.set_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept, Authorization, \
            X-Auth-Token, X-Custom-Header'
        )
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Max-Age', '3600')

    def write_error(self, status_code, **kwargs):

        if 'error' not in kwargs.keys():
            if (hasattr(self, '_reason') and self._reason) and \
                    (hasattr(self, '_status_code') and self._status_code):
                error = self._reason
                error_description = self._status_code
            else:
                error = self.http_codes['internal_error']['error'],
                error_description = self.http_codes['internal_error']\
                    ['error_description']
        else:
            error = self.http_codes[kwargs['error']]['error']
            error_description = self.http_codes[kwargs['error']]\
                ['error_description']

        self.finish(
            dict(
                error=error,
                error_description='%s: %s' % (
                    error_description,
                    kwargs['description']) if 'description' in kwargs.keys()\
                                              and kwargs['description']\
                                              else error_description
            )
        )

    def prepare(self):

        # Fields first
        self.fields = dict()
        if 'Content-Type' in self.headers.keys() and \
                self.headers['Content-Type'].lower() == 'application/json':
            try:
                self.fields = json.loads(self.request.body)
            except:
                raise self.utils.BaseExceptionError('invalid_json')

        else:
            self.fields = {k: self.utils.to_string(
                self.request.arguments.get(k)
            ) for k in self.request.arguments}

        # Check Token if exist
        self.access_token = token.check_oauth2_token(
            self.headers,
            self.redis_db_token,
            self.config['clients'],
            self.fields,
            self.request.remote_ip,
            self.request.log,
        )

    def send_base_error_exception(
            self,
            error,
            description=None
    ):
        self.request.log.http_code = self.http_codes[error]['code']
        self.request.log.error = self.http_codes[error]['error']

        # Check error is internal
        if error == 'internal_error':
            if isinstance(description, str):
                self.request.log._error(description)
            else:
                self.request.log._error(
                    '%s: %s' % (type(description), str(description))
                )
        else:
            self.request.log._info(
                '%s %s' % (
                    self.http_codes[error]['error_description'],
                    description
                )
            )

        if not self.application.settings.get('test_mode'):
            self.request.log.a_info(
                int(self.http_codes[error]['code']),
                self.http_codes[error]['error'],
                self.http_codes[error]['error_description']
            )

        self.send_error(
            int(self.http_codes[error]['code']),
            error=error,
            description=self.http_codes[error]['error_description']
        )
