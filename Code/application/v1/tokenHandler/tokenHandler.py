from application.v1.baseHandler.baseHandler import BaseHandler
import services.base_exception as base_exception
import services.token as token


class TokenHandler(BaseHandler):

    def prepare(self):
        try:
            super(TokenHandler, self).prepare()

            if 'client_id' not in self.fields.keys() or not\
                    self.fields['client_id'] or self.fields['client_id']\
                    not in self.config['clients'].keys():
                raise base_exception.BaseExceptionError\
                    ('unauthorized_client_id')

            if 'client_secret' not in self.fields.keys() or not\
                    self.fields['client_secret'] or\
                    str(self.fields['client_secret']) != \
                    self.config['clients'][self.fields['client_id']]['secret']:
                raise base_exception.BaseExceptionError\
                    ('unauthorized_client_secret')

            if 'token' not in self.fields.keys() or not self.fields['token']:
                raise base_exception.BaseExceptionError('missing_token')

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error, e.description)
        except Exception as e:
            self.send_base_error_exception(e, 'internal_error')

    def get(self):

        try:
            self.request.log._info('GET TokenHandler')

            atoken = token.load_token(
                self.fields['token'],
                self.redis_db_token,
                self.config['clients'],
                self.fields,
                self.request.remote_ip,
                self.request.log,
            )

            self.finish(atoken)

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error, e.description)
        except Exception as e:
            self.send_base_error_exception(e, 'internal_error')

    def post(self):

        try:
            if 'grant_type' not in self.fields.keys() or\
                    self.fields['grant_type'] not in\
                    ['refresh_token', 'revoke_token']:
                raise base_exception.BaseExceptionError('invalid_grant_type')

            self.request.log._info('POST TokenHandler')

            if self.fields['grant_type'] == 'refresh_token':
                self.refresh()
            else:
                self.revoke()

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error, e.description)
        except Exception as e:
            self.send_base_error_exception(e, 'internal_error')

    def refresh(self):

        try:
            self.request.log._info('refresh TokenHandler')
            atoken = token.load_token(
                self.fields['token'],
                self.redis_db_token,
                self.config['clients'],
                self.fields,
                self.request.remote_ip,
                self.request.log,
            )

            if atoken['type'] != 'refresh_token':
                raise base_exception.BaseExceptionError('invalid_token')

            # New token
            refresh_token = token.save_token(
                atoken['login'],
                atoken['client_id'],
                atoken['client_secret'],
                self.request.remote_ip,
                self.redis_db_token,
                self.server_config['grant']['token_expire'],
                self.request.log
            )

            # remove old token
            self.remove_token(atoken['access_token'], atoken['refresh_token'])

            self.finish(refresh_token)

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error, e.description)
        except Exception as e:
            raise base_exception.BaseExceptionError('internal_error', e)

    def remove_token(self, access_token=None, refresh_token=None):

        try:
            if access_token:
                self.redis_db_token.delete(access_token)
                self.request.log._info(
                    'Access Token Remove: %s' % access_token
                )

            if refresh_token:
                self.redis_db_token.delete(refresh_token)
                self.request.log._info(
                    'Refresh Token Remove: %s' % refresh_token
                )

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error, e.description)
        except Exception as e:
            raise base_exception.BaseExceptionError('internal_error', e)

    def revoke(self):

        try:
            self.request.log._info('revoke TokenHandler')

            atoken = token.load_token(
                self.fields['token'],
                self.redis_db_token,
                self.config['clients'],
                self.fields,
                self.request.remote_ip,
                self.request.log,
            )

            if atoken['type'] != 'access_token':
                raise base_exception.BaseExceptionError('invalid_token_type')

            self.remove_token(atoken['access_token'], atoken['refresh_token'])

            self.request.log._info('Token revoked')

            self.finish(dict())

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error, e.description)
        except Exception as e:
            raise base_exception.BaseExceptionError('internal_error', e)
