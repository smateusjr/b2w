import requests


class Swapi():

    url_api = "https://swapi.co/api/"
    search = "?search="

    def build_url_planets(self):
        """
        Cria a url para planetas
        """
        url_planets = requests.compat.urljoin(
            SwapiConnection.url_api,
            "planets/"
        )
        return url_planets

    def request_url(self, url):
        """Faz a request para o serviço
        """
        resp = requests.get(url)
        return resp.json()

    def get_planet_id(self, planet_id):
        """Retorna as informações de um planeta pelo id
        """
        url = self.build_url_planets()
        url = url + str(planet_id)
        json_data = self.request_url(url)
        return json_data

    def get_planet_name(self, planet_name):
        """Retorna as informações de um planeta pelo nome
        """
        url = self.build_url_planets()
        url = url + SwapiConnection.search + planet_name
        json_data = self.request_url(url)
        return json_data

    def count_apparitions(self, planet_name):
        """Retorna a quantidade de aparições dado um nome de um planeta
        """
        json_data = self.get_planet_name(planet_name)
        return len(json_data["results"][0]["films"])