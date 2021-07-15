# -*- coding: utf-8 -*-

import json
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime


class ZvooqApi(object):

    def __init__(self, url='', username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        self.success_status_code = [200, 201]
        self.unauthorized_status_code = [401]
        self.status_code_for_retry = [502, 503, 504, 422]
        self.auth_token = ''
        self.s = requests.Session()
        self.retries = Retry(total=5, backoff_factor=1, status_forcelist=self.status_code_for_retry)
        self.s.mount('https://', HTTPAdapter(max_retries=self.retries))

    # def __del__(self):
        # self.__logout()

    def get_url(self):
        return self.url

    def get_auth_token(self):
        return self.auth_token

    def request(self, method_url, method_type, headers=None, data=None, params=None, body=None):
        response = ''

        if headers is None:
            headers = {'x-auth-token': self.auth_token,
                       'Content-Type': 'application/x-www-form-urlencoded'}

        if method_type == 'get':
            response = self.__get(self.url + method_url, headers, params)
        elif method_type == 'post':
            response = self.__post(self.url + method_url, headers, data, params, body)
        elif method_type == 'put':
            response = self.__put(self.url + method_url, headers, params, body)
        elif method_type == 'delete':
            response = self.__delete(self.url + method_url, headers, params, body)
        return response

    def __get(self, url, headers, params=None):
        result = None

        try:
            response = self.s.get(url, headers=headers, params=params)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                self.stop_client()
                self.start_client()
                time.sleep(2)
                result = self.__get(url, params)

                # result = response.json()
                # if 'Message' in result:
                #     if result['Message'] == 'Unauthorized':
                #         self.stop_client()
                #         self.start_client()
                #         time.sleep(2)
                #         self.__get(url, params, headers)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __post(self, url, headers, data=None, params=None, body=None):
        result = None

        try:
            response = self.s.post(url, headers=headers, data=data, params=params, json=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                self.stop_client()
                self.start_client()
                time.sleep(2)
                result = self.__get(url, params)

                # result = response.json()
                # if 'Message' in result:
                #     if result['Message'] == 'Unauthorized':
                #         self.stop_client()
                #         self.start_client()
                #         time.sleep(2)
                #         self.__get(url, params, headers)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __put(self, url, headers, params=None, body=None):
        result = None

        try:
            response = self.s.put(url, headers=headers, params=params, data=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                self.stop_client()
                self.start_client()
                time.sleep(2)
                result = self.__get(url, params)

                # result = response.json()
                # if 'Message' in result:
                #     if result['Message'] == 'Unauthorized':
                #         self.stop_client()
                #         self.start_client()
                #         time.sleep(2)
                #         self.__get(url, params, headers)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __delete(self, url, headers, params=None, body=None):
        result = None

        try:
            response = self.s.delete(url, headers=headers, params=params, data=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                self.stop_client()
                self.start_client()
                time.sleep(2)
                result = self.__get(url, params)

                # result = response.json()
                # if 'Message' in result:
                #     if result['Message'] == 'Unauthorized':
                #         self.stop_client()
                #         self.start_client()
                #         time.sleep(2)
                #         self.__get(url, params, headers)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __login(self):
        method_url = 'api/tiny/login/email'
        data = {'email': self.username,
                'password': self.password}
        response = self.request(method_url=method_url, method_type='post', data=data)
        if response is not None and 'result' in response:
            self.auth_token = response['result']['token']
            print('INFO: ' + str(datetime.now()) + ' ' + self.url + ' Token: ' + self.auth_token)

    def __logout(self):
        method_url = 'auth/api/v1/Logout/'
        response = self.request(method_url=method_url, method_type='post')
        if response is not None:
            print('INFO: ' + str(datetime.now()) + ' Atlas connection ' + self.url + ' closed')

    def start_client(self):
        print('INFO: ' + str(datetime.now()) + ' Zvooq connection ' + self.url + ' connects')
        if self.auth_token == '':
            self.__login()

    def stop_client(self):
        # self.__logout()
        self.s.close()

    '''Search playlists'''
    def search_playlists(self, query: str, suggest=False, limit=50, type='playlist'):
        method_url = 'api/tiny/search?suggest=' + str(suggest) + '&limit=' + str(limit) + '&type=' + type +\
                     '&query=' + query
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nPlaylists searching failed')
        return response

    '''Search playlists'''
    def search_playlists_sapi(self, query: str, limit=50, include='playlist'):
        method_url = 'sapi/search?query=' + query + '&limit=' + str(limit) + '&include=' + include
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nPlaylists searching failed')
        return response

    '''Search tracks'''
    def search_tracks(self, query: str, limit=50, include='track'):
        method_url = 'sapi/search?query=' + query + '&limit=' + str(limit) + '&include=' + include
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nTracks searching failed')
        return response

    '''Get playlists'''
    def get_playlists(self, playlist_ids: [str]):

        string = ''
        for i, playlist_id in enumerate(playlist_ids):
            string += playlist_id + ','
            if i == len(playlist_ids) - 1:
                string += playlist_id

        method_url = 'api/tiny/playlists?ids=' + string
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nPlaylists receiving failed')
        return response

    '''Get stream'''
    def get_track_stream(self, track_id: str, quality='high'):
        method_url = 'api/tiny/track/stream?id=' + track_id + '&quality=' + quality
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nStream receiving failed')
        return response

    '''Create order'''
    # def create_order(self, op_type='Delivery', hub_code='01-01-КЛМ', route_external_id=None, carrier_code=None,
    #                  leg_external_id=None, delivery_from='2020-01-01T10:00:00.000Z',
    #                  delivery_to='2020-01-01T12:00:00.000Z', load_from='', load_to=''):
    #     order_number = 'OTBG-' + str(datetime.now())
    #     method_url = 'oms/api/Orders'
    #     body = {
    #                 "OrderInfo": {
    #                     "ExternalId": order_number,
    #                     "Number": order_number,
    #                     "OperationType": op_type
    #                 },
    #                 "AllocationInfo": {
    #                     "HubCode": hub_code,
    #                     "RouteExternalId": route_external_id,
    #                     "CarrierCode": carrier_code,
    #                     "TacticalLegExternalId": leg_external_id
    #                 },
    #                 "DeliveryTimeSlot": {
    #                     "From": delivery_from,
    #                     "To": delivery_to
    #                 },
    #                 # "LoadTimeSlot": {
    #                 #     "From": load_from,
    #                 #     "To": load_to
    #                 # },
    #                 "ContactInfo": {
    #                     "Name": "Иванов Иван Иванович",
    #                     "Phones": [
    #                         "+79999999999"
    #                     ]
    #                 },
    #                 "AddressInfo": {
    #                     "FullAddress": "Rue du Saint-Gothard, 11, Strasbourg, Франция. 67000",
    #                     "Country": "Россия",
    #                     "PostalCode": "193315",
    #                     "District": "Санкт-Петербург",
    #                     "Town": "Санкт-Петербург",
    #                     "Street": "проспект Большевиков",
    #                     "Building": "42"
    #                 },
    #                 "TransportRestrictionsInfo": {
    #                     "LoadUnloadTypes": [
    #                         "BothSide"
    #                     ],
    #                     "TransportRestrictions": ["MKAD"]
    #                 }
    #             }
    #     response = self.request(method_url=method_url, method_type='post', body=body)
    #     if response is None:
    #         print('\nOrder creating failed')
    #     return response