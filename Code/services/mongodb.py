from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
from bson import json_util
import services.base_exception as base_exception


class mongoDB():

    def __init__(self, url, port, database, colletion):
        self.client = MongoClient(url, port)
        self.database = self.client[database]
        self.colletion = self.database[colletion]

    def planet_save(self, data):
        planet_id = self.colletion.insert_one(data).inserted_id
        return planet_id

    def planet_list(self, search=None, skips=None, r_by_page=None):
        result = dict()
        if not search:
            if type(skips) is int and type(r_by_page) is int:
                planets_list = self.colletion.find().skip(skips).limit(
                    r_by_page
                )
            else:
                planets_list = self.colletion.find()

            for planet in planets_list:
                self.parse_result(result, planet)
        else:
            planet = self.colletion.find_one(search)

            self.parse_result(result, planet)

        return result

    def planet_delete(self, search):
        result = dict()
        planet_list = self.colletion.find_one(search)
        if not planet_list:
            raise base_exception.BaseExceptionError('not_found')
        planet = self.colletion.find_one_and_delete(search)
        self.parse_result(result, planet)
        return result

    def parse_result(self, result, data):
        if data:
            result.update(
                {
                    data['_id'].__str__(): json.loads(
                        json_util.dumps(
                            data
                        )
                    )
                }
            )

    def check_status(self):
        try:
            self.client.admin.command('ismaster')
            return True
        except ConnectionFailure:
            return False
