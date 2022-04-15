import requests
import json
from datetime import timedelta
from datetime import datetime


def interval(func: callable):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        interval = args
        print("requesting " + interval[1] + " - " + interval[2])
        return res

    return wrapper


def minus_day_from_end(delta):
    def pseudo_decorator(func: callable):
        def wrapper(self, start, end):
            end = datetime.strptime(end, '%Y-%m-%d')
            end = str(end.date() - delta)
            res = func(self, start, end)
            return res

        return wrapper

    return pseudo_decorator


class BTCApi:

    @minus_day_from_end(delta=timedelta(days=1))
    @interval
    def make_request(self, start, end):
        response_data = requests.get('https://api.coindesk.com/v1/bpi/historical/close.json',
                                     params={'start': start, 'end': end})
        raw_response = json.loads(response_data.content)
        response = raw_response['bpi']
        return response

    def put_req_data_to_dict(self, data_from_db: dict, start, end):
        dates = self.make_request(start, end)
        for date, price in dates.items():
            data_from_db[date] = price
