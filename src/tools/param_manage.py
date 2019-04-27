# -*- coding: utf-8 -*-

import json

#full_path = dirname(dirname(dirname(abspath(__file__))))  # /../../../
file_path = 'config/config.json' 


# Open json-file for read
def readConfig():
    #file_path = full_path+'/congig/config.json'
    with open(file_path, 'r') as f:
        data = json.loads(f.read())
    return data


# Write to json-file
def editConfig(data):
    #file_path = full_path+'/congig/config.json'
    with open(file_path, 'w') as f:
        json.dump(data, f)


# Read detection parameters
def getDetectionParameters():
    data = readConfig()

    MIN_AREA = data['DetectionParameters']['min_area']
    BLUR_SIZE = data['DetectionParameters']['blur_size']
    BLUR_POWER = data['DetectionParameters']['blur_power']
    THRESHOLD_LOW = data['DetectionParameters']['threshold_low']

    return MIN_AREA, BLUR_SIZE, BLUR_POWER, THRESHOLD_LOW


# Edit detection parameters
def setDetectionParameters(MIN_AREA, BLUR_SIZE, BLUR_POWER, THRESHOLD_LOW):   
    data = readConfig()
    
    data['DetectionParameters']['min_area'] = MIN_AREA
    data['DetectionParameters']['blur_size'] = BLUR_SIZE
    data['DetectionParameters']['blur_power'] = BLUR_POWER
    data['DetectionParameters']['threshold_low'] = THRESHOLD_LOW
    
    editConfig(data)
    
    
# Read bot parameters
def getBotParameters():
    data = readConfig()
    
    BOT_TOKEN = data['BotParameters']['token'] # bot token
    PROXY_URL = data['BotParameters']['proxy_url'] # proxy-server address
    MY_CHAT_ID = data['BotParameters']['chat_id'] # chat id with bot
    SENDING_PERIOD = data['BotParameters']['sending_period'] # message sending period in to chat by bot
    USERNAME = data['BotParameters']['username'] # proxy username
    PASSWORD = data['BotParameters']['password'] # proxy password

    # Proxy parameters
    REQUEST_KWARGS={'proxy_url': PROXY_URL}
    
    return BOT_TOKEN, REQUEST_KWARGS, MY_CHAT_ID, PROXY_URL, SENDING_PERIOD, USERNAME, PASSWORD


# Edit bot parameters
def setBotParameters(BOT_TOKEN, PROXY_URL, MY_CHAT_ID, SENDING_PERIOD, USERNAME, PASSWORD):   
    data = readConfig()
    
    data['BotParameters']['token'] = BOT_TOKEN # bot token
    data['BotParameters']['proxy_url'] = PROXY_URL # proxy-server address
    data['BotParameters']['chat_id'] = MY_CHAT_ID # chat id with bot
    data['BotParameters']['sending_period'] = SENDING_PERIOD # message sending period in to chat by bot
    data['BotParameters']['username'] = USERNAME # proxy username
    data['BotParameters']['password'] = PASSWORD # proxy password
    
    editConfig(data)


# Read NN parameters
def getNNParameters():
    data = readConfig()

    NET_ARCHITECTURE = data['NNParameters']['net_architecture'] # net architecture
    NET_MODEL = data['NNParameters']['net_model'] # net model
    CLASSES = data['NNParameters']['classes'] # classes
    CONFIDENCE = data['NNParameters']['confidence'] # confidence

    return NET_ARCHITECTURE, NET_MODEL, CLASSES, CONFIDENCE
