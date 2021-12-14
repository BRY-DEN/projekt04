import json
from urllib.parse import urljoin
from typing import Dict, List, Union, Any

import requests


class BRRealEstateOffer:
    """Create a new object from the given attributes."""
    offer_count: int = 0

    def __init__(self, details: Dict[str, Any]):
        self.id_ = details.get("id")
        self.date = details.get("date")
        self.url = details.get("url")
        self.gps = details.get("gps")
        self.price = details.get("price")
        self.surface = details.get("surface")
        self.currency = details.get("currency")
        self.surface_land = details.get("surfaceLand")
        self.key_offer_type = details.get("keyOfferType")
        self.key_estate_type = details.get("keyEstateType")
        self.key_disposition = details.get("keyDisposition")

    @classmethod
    def add_offer(cls):
        cls.offer_count += 1

    def __repr__(self) -> str:
        return str(f"{self.url}")

    # date of offer added, output restructured and modified
    def full_description(self) -> str:
        return f"{self.date[:19]}; {format(self.price, ',d')} {self.currency}; {self.key_offer_type}; {self.key_estate_type}; {self.key_disposition}; {self.surface}m2; {self.url}"

class ScraperInitiator:
    """Initiate a new object for the data transfer."""

    def __init__(self, url: str, params: Dict[str, str]):
        self.url = url
        self.params = params

    def send_post_request(self) -> requests.models.Response:
        return requests.post(self.url, params=self.params)

    @staticmethod
    def load_json(response: requests.models.Response) -> List[Dict[str, str]]:
        """Load the 'json' package and read the content from string."""
        return json.loads(response.text)


session_1 = ScraperInitiator(
    "https://www.bezrealitky.cz/api/record/markers",
    {
         'offerType': 'prodej',  # other options: prodej, pronajem, spolubydleni
        # 'estateType': 'byt',
        # 'disposition': '3-kk'
        # 'submit': '1', ??? usage?
        # 'boundary': '[[[{"lat":52,"lng":12},{"lat":52,"lng":16},{"lat":50,"lng":16},{"lat":50,"lng":12},{"lat":52,"lng":12}]]]',  # this polygon (rectangle) makes no sence, according to google maps is partly in Germany, Prague excluded
         'boundary': '[[[{"lat":50,"lng":11},{"lat":51,"lng":15},{"lat":49,"lng":19},{"lat":47,"lng":14},{"lat":50,"lng":11}]]]', # CZ
        # 'boundary': '[[[{"lat":49,"lng":19},{"lat":48,"lng":23},{"lat":47,"lng":19},{"lat":48,"lng":16},{"lat":49,"lng":19}]]]'  # SK
    }
)

json_: List[Dict[str, Any]] = session_1.load_json(
    session_1.send_post_request()
)


class DataParser:
    """Parse the given data and create cleaner, non-nested python object."""

    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.url: str = "https://www.bezrealitky.cz/nemovitosti-byty-domy/"



    def iterate_through_data(self):
        results: list = []

        for offer in self.data:
            uri, details = self.parse_main_dict(offer)
            results.append(
                self.extend_dict(url=urljoin(self.url, uri), date=offer.get("timeOrder", {}).get("date"), details=details)
            )

        return results

    @staticmethod
    def parse_main_dict(offer: Dict[str, Any]) -> tuple:
        """Parse and return attributes uri, advertEstateOffer."""
        return offer.get("uri"), offer.get("advertEstateOffer")[0]

    @staticmethod
    def extend_dict(**kwargs):
        """Create and update a new dictionary object with the given attrs."""
        attributes: Dict[str, str] = {}

        for key, val in kwargs.items():
            if key in ("url", "date"):
                attributes[key] = val
            else:
                attributes.update(val)

        return attributes


parser_1 = DataParser(json_)
testing_list = parser_1.iterate_through_data()


class BRRealEstateOfferProcessor:
    """Process the given attributes and a new object 'BRRealEstateOffer'."""

    def __init__(self, parsed_data: List[Dict[str, Union[str, int]]]):
        self.offers: list = []
        self.parsed_data = parsed_data

    def add_offer(self, dict_data: Dict[str, Union[str, int]]) -> None:
        self.offers.append(
            BRRealEstateOffer(dict_data)
        )

    def process_offers(self) -> None:
        for offer in self.parsed_data:
            self.add_offer(offer)


def run_collector():
    proc_1 = BRRealEstateOfferProcessor(testing_list)
    proc_1.process_offers()
    return proc_1.offers

