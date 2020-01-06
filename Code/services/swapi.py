import requests
import services.base_exception as base_exception


class Swapi():

    def __init__(self, url_swapi, redis_db_swapi, expire):
        self.url_swapi = url_swapi
        self.redis_db_swapi = redis_db_swapi
        self.expire = expire

    def get_qtd_planet_by_name(self):
        try:
            qtd_planet_film = self.check_cache_swapi(self.url_swapi)
            if qtd_planet_film:
                return qtd_planet_film
            else:
                swapi_request = requests.get(self.url_swapi, timeout=1)
                swapi_request.raise_for_status()
                swapi_response = swapi_request.json()
                qtd_planet_film = len(swapi_response['results'][0]['films'])

                # Save in redis
                self.redis_db_swapi.setex(
                    self.url_swapi,
                    self.expire,
                    int(qtd_planet_film)
                )
                return qtd_planet_film

        except base_exception.BaseExceptionError as e:
            raise base_exception.BaseExceptionError(e.error)
        except Exception as e:
            raise base_exception.BaseExceptionError('internal_error', e)

    def check_cache_swapi(self, url):
        try:
            get_redis_swapi = self.redis_db_swapi.get(url)
            if get_redis_swapi:
                swapi_load = eval(get_redis_swapi.decode(),
                                  {'false': False, 'true': True, 'Null': None,
                                   'null': None, '__builtins__': {}})
                return swapi_load
            return None
        except base_exception.BaseExceptionError as e:
            raise base_exception.BaseExceptionError(e.error)
        except Exception as e:
            raise base_exception.BaseExceptionError('internal_error', e)
