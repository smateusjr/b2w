from application.v1.baseHandler.baseHandler import BaseHandler

import services.base_exception as base_exception
import services.token as token


class AuthorizationHandler(BaseHandler):

    def prepare(self):
        try:
            super(AuthorizationHandler, self).prepare()
            self.request.log.body = None
            self.client_id = None

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error)
        except Exception as e:
            self.send_base_error_exception('internal_error', e)

    def post(self):

        self.request.log._info('Authorization')
        try:

            # Check client_id
            if 'client_id' not in self.fields.keys() or not\
                    self.fields['client_id'] or self.fields['client_id']\
                    not in self.config['clients'].keys():
                raise base_exception.BaseExceptionError\
                    ('unauthorized_client_id')

            # Check login
            if 'login' not in self.fields.keys() or not self.fields['login']\
                    or str(self.fields['login']) not in\
                    self.config['clients'][self.fields['client_id']]['logins']\
                            .keys():
                raise base_exception.BaseExceptionError('unauthorized_user')

            # Check password
            if 'password' not in self.fields.keys() or not\
                    self.fields['password'] or str(self.fields['password'])\
                    != self.config['clients'][self.fields['client_id']]\
                    ['logins'][self.fields['login']]:
                raise base_exception.BaseExceptionError('invalid_password')

            get_token = token.save_token(
                self.fields['login'],
                self.fields['client_id'],
                self.config['clients'][self.fields['client_id']]['secret'],
                self.request.remote_ip,
                self.redis_db_token,
                self.server_config['grant']['token_expire'],
                self.request.log
            )
            self.finish(get_token)

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error, e.description)
        except Exception as e:
            self.send_base_error_exception('internal_error', e)
