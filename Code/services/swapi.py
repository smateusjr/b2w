import requests
import services.base_exception as base_exception


class Swapi():

    def __init__(self, url_swapi):
        self.url_swapi = url_swapi

    def get_planet_by_name(self):
        try:
            swapi_request = requests.get(self.url_swapi, timeout=1)
            swapi_request.raise_for_status()
            swapi_response = swapi_request.json()
            return len(swapi_response['results'][0]['films'])

        except base_exception.BaseExceptionError as e:
            raise base_exception.BaseExceptionError(e.error)
        except Exception as e:
            raise base_exception.BaseExceptionError('internal_error', e)
