import json
import os
import requests
import sys

__author__ = 'Pontus'


class CharonConnection(object):

    def __init__(self, projectid=None):
        self.projectid = projectid
        self.session = requests.Session()
        self.headers = {'X-Charon-API-token': os.getenv('CHARON_API_TOKEN'),'content-type': 'application/json'}
        self.base_url = "{}/api/v1".format(os.getenv('CHARON_BASE_URL').replace('-dev',''))

    def delivered_samples(self):
        query_url = "{}/customquery".format(self.base_url)
        query = {'projectid': self.projectid,
                 'sampleField': 'delivery_status',
                 'operator': '==',
                 'value': 'DELIVERED',
                 'type': 'unicode'}
        return self.session.get(query_url, data=json.dumps(query), headers=self.headers).json().get('samples')

if __name__ == '__main__':
    for sample in CharonConnection(projectid=sys.argv[1]).delivered_samples():
        print(sample.get('sampleid') + " " + sample.get('delivery_status'))
