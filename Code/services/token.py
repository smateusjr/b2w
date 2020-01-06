from oauthlib import common
import services.base_exception as base_exception


def save_token(
        login,
        client_id,
        client_secret,
        ip,
        redis_db_token,
        token_expire,
        log
):
    try:
        access_tmp = common.generate_token()
        refresh_tmp = common.generate_token()

        # Dict token base
        token_save = dict(
            login=login,
            client_id=client_id,
            client_secret=client_secret,
            ip=ip,
            refresh_token=refresh_tmp,
            access_token=access_tmp
        )
        # make refresh token
        token_save_refresh = token_save.copy()
        token_save_refresh.update(
            type="refresh_token"
        )
        redis_db_token.set(refresh_tmp, str(token_save_refresh))

        # make access token
        token_save.update(
            type="access_token",
            expires=token_expire
        )
        redis_db_token.setex(access_tmp, token_save['expires'], str(token_save))

        log._info(
            'Access Token e Refresh Token Save: %s - %s - %s' % (
            access_tmp, refresh_tmp, token_save))

        return dict(
            access_token=access_tmp,
            refresh_token=refresh_tmp,
            expires_in=token_save['expires']
        )

    except Exception as e:
        raise base_exception.BaseExceptionError('internal_error', e)


def load_token(token, redis_db_token, config_clients, fields, ip, log):
    try:
        get_redis_token = redis_db_token.get(token)

        if get_redis_token:
            token_load = eval(get_redis_token.decode(),
                              {'false': False, 'true': True, 'Null': None,
                               'null': None, '__builtins__': {}})

            log._info('Token Load: %s' % token, {'token': token_load})

            if token_load['client_id'] != fields['client_id']:
                raise base_exception.BaseExceptionError\
                    ('unauthorized_client_id')

            if token_load['client_secret'] != fields['client_secret']:
                raise base_exception.BaseExceptionError\
                    ('unauthorized_client_secret')

            if token_load['login'] not in \
                    config_clients[token_load['client_id']][
                        'logins'].keys():
                raise base_exception.BaseExceptionError('unauthorized_user')

            if token_load['ip'] != ip:
                raise base_exception.BaseExceptionError('invalid_token')

            return token_load

        else:
            raise base_exception.BaseExceptionError('invalid_token')

    except base_exception.BaseExceptionError as e:
        raise base_exception.BaseExceptionError(e.error)
    except Exception as e:
        raise base_exception.BaseExceptionError('internal_error', e)


def check_oauth2_token(headers, redis_db_token, config_clients, fields, ip, log):
    auth = headers.get('Authorization')
    if auth:
        token = load_token(
            auth,
            redis_db_token,
            config_clients,
            fields,
            ip,
            log,
        )
        return token

    return None
