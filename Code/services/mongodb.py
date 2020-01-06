from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class mongoDB():

    def __init__(self, url, port, database, colletion):
        self.client = MongoClient(url, port)
        self.database = self.client[database]
        self.colletion = self.database[colletion]

    def return_planet_collection(self):
        return self.colletion.planets

    def planet_save(self, data):
        """
        Save planet
        """

        planet_id = self.colletion.insert_one(data).inserted_id
        return planet_id

    def planet_list(self):
        """
        List planet
        """
        planets = self.colletion.planets
        planets_list = planets.find()
        return planets_list

    def planet_list_by_id(self, planet_id):
        """
        List planet by id
        """
        planets = self.colletion.planets
        planet = planets.find_one({"id": planet_id})
        return planet

    def planet_list_by_name(self, planet_name):
        """
        List planet by name
        """
        planets = self.colletion.planets
        planet = planets.find_one({"planet_name": planet_name})
        return planet

    def planet_delete_by_id(self, planet_id):
        """
        Delete by id
        """
        planets = self.colletion.planets
        planet = planets.find_one_and_delete({"id": planet_id})
        return planet

    def planet_by_name(self, planet_name):
        """
        Delete by name
        """
        planets = self.colletion.planets
        planet = planets.find_one_and_delete({"planet_name": planet_name})
        return planet

    def get_last(self):
        """
        Get last register
        """
        planets = self.colletion.planetas
        planets_list = planets.find().limit(1).sort([{'$natural', -1}])
        last = []
        for planet in planets_list:
            last.append(planet)
        return last

    def check_status(self):
        """
        Check Mongo Status
        """
        try:
            self.client.admin.command('ismaster')
            return True
        except ConnectionFailure:
            return False
