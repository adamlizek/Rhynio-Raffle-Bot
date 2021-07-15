from pymongo import MongoClient
from requests import get
import config as CONFIG

# Storing URI in the code is bad practice but this is old code ok
CLIENT = MongoClient("REMOVED")
DB = CLIENT['RhynioRaffles']
RAFFLE_DATA = DB.Active_Raffles


def get_active_raffles(site):

    query_result = RAFFLE_DATA.find({'site': site})

    return query_result


def get_specific_raffle(site, raffle_name):
    query_result = RAFFLE_DATA.find_one({"site": site,
                                         "name": raffle_name
                                         })

    return query_result
