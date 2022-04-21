import requests
import json


def interval(func: callable):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        interval = args
        print("requesting " + interval[1] + " - " + interval[2])
        with open('newfile.txt', 'a+', encoding='utf-8') as file:
            file.writelines(interval[1] + " - " + interval[2] + "\n")
        return res

    return wrapper


class BTCApi:

    @interval
    def make_request(self, start, end):
        response_data = requests.get('https://api.coindesk.com/v1/bpi/historical/close.json',
                                     params={'start': start, 'end': end})
        raw_response = json.loads(response_data.content)
        response = raw_response['bpi']
        return response

    def put_req_data_to_dict(self, data_from_db: dict, start, end):
        #сделать абстрактное название параметра data_from_db
        dates = self.make_request(start, end)
        for date, price in dates.items():
            data_from_db[date] = price
