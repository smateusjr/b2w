from application.v1.baseHandler.baseHandler import BaseHandler
import services.base_exception as base_exception
from bson import ObjectId

# Swapi
import services.swapi as swapi

# Mongodb
import services.mongodb as mongo


class PlanetHandler(BaseHandler):

    def prepare(self):

        try:
            super(PlanetHandler, self).prepare()

            # mongo
            self.mongodb = mongo.mongoDB(
                self.server_config['mongodb']['host'],
                int(self.server_config['mongodb']['port']),
                self.server_config['mongodb']['database'],
                self.server_config['mongodb']['colletion']
            )
            self.mongodb.check_status()

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error)
        except Exception as e:
            self.send_base_error_exception('internal_error', e)

    def get(self):

        self.request.log._info('GET Planet')
        try:
            r_by_page = None
            skips = None
            q_params = dict()

            if 'id_planet' in self.fields.keys() and self.fields['id_planet']:
                if ObjectId.is_valid(self.fields['id_planet']):
                    q_params.update(_id=ObjectId(self.fields['id_planet']))
                else:
                    raise base_exception.BaseExceptionError('invalid_id')

            if 'name' in self.fields.keys() and self.fields['name'].isalnum():
                q_params.update(
                    name={'$regex': self.fields['name'], '$options': 'i'}
                )

            if 'result_by_page' in self.fields.keys() and self.fields[
                'result_by_page'] and self.fields['result_by_page'].isdigit()\
                    and 'n_page' in self.fields.keys() and\
                    self.fields['n_page'] and self.fields['n_page'].isdigit():
                skips = int(self.fields['result_by_page']) *\
                        (int(self.fields['n_page']) - 1)
                r_by_page = int(self.fields['result_by_page'])

            planet_list = self.mongodb.planet_list(q_params, skips, r_by_page)

            self.finish(planet_list)

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error)
        except Exception as e:
            self.send_base_error_exception('internal_error', e)

    def post(self):

        self.request.log._info('POST Planet')
        try:

            if ('name' not in self.fields.keys() or not self.fields['name'])\
                or ('climate' not in self.fields.keys() or not\
                    self.fields['climate']) or\
                    ('terrain' not in self.fields.keys() or not\
                    self.fields['terrain']):
                raise base_exception.BaseExceptionError('missing_fields')

            # check qtd_films
            if 'qtd_films' in self.fields and self.fields['qtd_films'] and \
                    self.fields['qtd_films'].isdigit():
                qtd_films = self.fields['qtd_films']
            else:
                ext_swapi = swapi.Swapi(
                    '%s%s' % (
                        self.server_config['swapi']['url'],
                        self.fields['name']
                    ),
                    self.redis_db_swapi,
                    self.server_config['grant']['swapi_expire']
                )
                qtd_films = ext_swapi.get_qtd_planet_by_name()
            data = dict(
                name=self.fields['name'],
                climate=self.fields['climate'],
                terrain=self.fields['terrain'],
                qtd_films=qtd_films
            )
            id_planet = self.mongodb.planet_save(data)

            self.finish(
                dict(id=id_planet.__str__())
            )

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error)
        except Exception as e:
            self.send_base_error_exception('internal_error', e)

    def delete(self):

        self.request.log._info('DELETE Invoice')
        try:
            q_params = dict()

            if 'id_planet' not in self.fields.keys() or not \
                    self.fields['id_planet']:
                raise base_exception.BaseExceptionError('missing_fields')
            if not ObjectId.is_valid(self.fields['id_planet']):
                raise base_exception.BaseExceptionError('not_found')

            q_params.update(_id=ObjectId(self.fields['id_planet']))

            planet_delete = self.mongodb.planet_delete(q_params)

            self.finish(planet_delete)

        except base_exception.BaseExceptionError as e:
            self.send_base_error_exception(e.error)
        except Exception as e:
            self.send_base_error_exception('internal_error', e)
