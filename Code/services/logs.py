import uuid
import time
import json
import logging
import logging.config
import datetime
from collections import OrderedDict


class LogClass(object):

    def __init__(self, path, propagate=True):
        self.request_id = uuid.uuid4().hex
        self.time_start_at = time.time()
        self.start_time = datetime.datetime.now()
        self.client_id = ""
        self.error = ""
        self.http_code = ""
        self.path = ""
        self.uri = ""
        self.body = ""
        self.ip = ""
        self.headers = ""
        self.query = ""

        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '%(asctime)s [%(levelname)s] %(message)s'
                }
            },
            'loggers': {
                'root': {
                    'level': 'INFO',
                    'handlers': ['console'],
                },
                'planet': {
                    'level': 'INFO',
                    'handlers': ['planet'],
                    'propagate': propagate,
                },
                'access': {
                    'level': 'INFO',
                    'handlers': ['access'],
                    'propagate': propagate
                },
                'tornado.access': {
                    'level': 'ERROR',
                    'propagate': propagate
                },
                'tornado.general': {
                    'level': 'ERROR',
                    'propagate': propagate
                },
                'tornado.application': {
                    'level': 'ERROR',
                    'propagate': propagate
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'NOTSET',
                    'formatter': 'default'
                },
                'planet': {
                    'class': 'logging.FileHandler',
                    'level': 'INFO',
                    'formatter': 'default',
                    'filename': "%s/planet.log" % path
                },
                'access': {
                    'class': 'logging.FileHandler',
                    'level': 'INFO',
                    'formatter': 'default',
                    'filename': "%s/access.log" % path
                }
            }
        })

        self.planet = logging.getLogger('planet')
        self.access = logging.getLogger('access')

    def _info(self, message, extra=None):
        to_parse = {
            'description': message
        }
        if extra:
            to_parse.update(extra)
        self.planet.info(json.dumps(self._parse_log(to_parse)))

    def _error(self, data):
        to_parse = {
            'description': data
        }
        self.planet.error(json.dumps(self._parse_log(to_parse)))

    def a_info(self, http_code, error="", error_description=""):
        self.access.info(
            json.dumps(
                self._parse_access(
                    dict(
                        http_code=http_code,
                        error=error,
                        error_description=error_description
                    )
                )
            )
        )

    def _parse_log(self, json):
        json['execution_time'] = str(
            datetime.timedelta(seconds=time.time() - self.time_start_at)
        )
        json['request_id'] = self.request_id
        json['ip'] = self.ip
        json['start_time'] = str(self.start_time)
        json['path'] = self.path
        json['uri'] = self.uri
        json['headers'] = self.headers

        if self.error:
            json['error'] = self.error
        if self.http_code:
            json['http_code'] = self.http_code

        return OrderedDict(json)

    def _parse_access(self, json):

        json['execution_time'] = str(
            datetime.timedelta(seconds=time.time() - self.time_start_at)
        )
        json['request_id'] = self.request_id
        json['ip'] = self.ip
        json['start_time'] = str(self.start_time)

        return OrderedDict(json)

    def set_body(self, headers, request):
        self.headers = headers
        self.path = request.path
        self.uri = request.uri
        self.ip = request.remote_ip
        self.body = request.body
        self.query = request.query
