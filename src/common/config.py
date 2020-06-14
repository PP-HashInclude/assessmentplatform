import configparser
import json

config = configparser.ConfigParser()

with open('data/config.json', 'r') as f:
    config = json.load(f)

def getdbfile():
    return config['DEFAULT']['DB_FILE']

def get(section, keyname):
    # print("CONFIG SECTION: ", config[section])
    return config[section][keyname]

def getSMSURL():
    # print(config['DEFAULT']['BULKSMS_URL'])
    return config['DEFAULT']['BULKSMS_URL']