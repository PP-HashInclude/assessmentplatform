import configparser
import json
import os
from common import utility

config = configparser.ConfigParser()

#with open('data/config.json', 'r') as f:
#    config = json.load(f)

b64config_data = os.environ.get("KSVSS_CONFIG")
config = utility.degenerateb64String(b64config_data)

def getdbfile():
    return config['DEFAULT']['DB_FILE']

def get(section, keyname):
    # print("CONFIG SECTION: ", config[section])
    return config[section][keyname]

def getSMSURL():
    # print(config['DEFAULT']['BULKSMS_URL'])
    return config['DEFAULT']['BULKSMS_URL']