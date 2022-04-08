import requests
import json


class BTCApi:

    def make_request(self, start, end):
        response_data = requests.get('https://api.coindesk.com/v1/bpi/historical/close.json',
                                     params={'start': start, 'end': end})
        raw_response = json.loads(response_data.content)
        response = raw_response['bpi']
        return response
