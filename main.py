from API import BTCApi
from DB import DataStorage
from Plot import plotData
from datetime import datetime
from datetime import timedelta
import argparse


def make_date_of_string(date: str):
    dates = {}
    dates['year'], dates['month'], dates['day'] = date.split('-')
    for key, item in dates.items():
        if item.startswith("0"):
            item = item.replace("0", "")
        dates[key] = int(item)
    date = datetime(day=dates['day'], month=dates['month'], year=dates['year'])
    return date


def search_first_valid_date(api: BTCApi, start, end):
    try:
        api.make_request(str(start.date()), str(start.date()))
        return start
    except:
        # бинарный поиск
        delta = (end - start) / 2
        start += delta
        while True:
            if delta.days < 1:
                try:
                    api.make_request(str(start.date()), str(start.date()))
                    return start
                except:
                    try:
                        api.make_request(str(end.date()), str(end.date()))
                        return end
                    except:
                        return None
            try:
                api.make_request(str(start.date()), str(start.date()))
                end = start
                start -= delta
                delta = (end - start) / 2
                start += delta
                print(start)
                print(end)
                # поиск в меньшей половине
            except:
                delta = (end - start) / 2
                start += delta
                print(start)
                print(end)
                # поиск в большей половине


def default_getting_data_from_server(data_from_db:dict, start:datetime, end:datetime, n_days:timedelta, api:BTCApi,
                    db:DataStorage):
    start_date_req = start

    while True:
        end_date_req = start_date_req + n_days

        if end_date_req >= end:
            end_date_req = end
            print("making request")
            data = api.make_request(str(start_date_req.date()), str(end_date_req.date()))
            for date, price in data.items():
                data_from_db[date] = price
            print(data)
            break
        print("making request")
        data = api.make_request(str(start_date_req.date()), str(end_date_req.date()))
        for date, price in data.items():
            data_from_db[date] = price
        print(data)
        start_date_req = end_date_req

    db.load_to_database(data_from_db)
    return data_from_db

def minimizing_data(data_from_db:dict, start:datetime, end:datetime, n_days:timedelta, api:BTCApi,
                    db:DataStorage):
    curr_date = start
    one_day = timedelta(days=1)
    counter = 0
    start_api_date = curr_date
    while True:
        if str(curr_date.date()) not in data_from_db:
            if counter == 0:
                start_api_date = curr_date
                counter += 1
            elif counter == n_days.days:
                dates = api.make_request(str(start_api_date.date()), str(curr_date.date()))
                for date, price in dates.items():
                    data_from_db[date] = price
                counter = 0
            if curr_date == end:
                dates = api.make_request(str(start_api_date.date()), str(curr_date.date()))
                for date, price in dates.items():
                    data_from_db[date] = price
                break
            else:
                counter += 1
        else:
            if counter != 0:
                end_api_date = curr_date - one_day
                dates = api.make_request(str(start_api_date.date()), str(end_api_date.date()))
                for date, price in dates.items():
                    data_from_db[date] = price
            if curr_date == end:
                break
            counter = 0

        curr_date += one_day

    db.load_to_database(data_from_db)
    return data_from_db


def minimizing_requests():
    pass


# парсинг аргументов из командной строки
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-start_date', type=str, help='input start date in format yyyy-mm-dd')
parser.add_argument('-end_date', type=str, help='input end date in format yyyy-mm-dd')
parser.add_argument('-n', type=int, help='input maximum amount of days in one request, n <= 100')
parser.add_argument('-first_valid_date', default=False, type=bool, help='finds first valid date in the interval')
parser.add_argument('-mode', type=str,
                    help='minimizes amount of requested data (min_data) or amount of requests (min_req')

args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date
n = args.n
n_days = timedelta(n)
first_valid_date_flag = args.first_valid_date
mode = args.mode

# объявление объектов классов
db = DataStorage("btc_tracker")
api = BTCApi()
plot = plotData()

start = make_date_of_string(start_date)
end = make_date_of_string(end_date)
time = end - start
amount_of_dates = time.days
data_from_db = db.get_from_database(start_date, end_date)

# поиск первой валидной даты
first_valid_date = search_first_valid_date(api, start, end)
if first_valid_date == None:
    print("Заданный интервал невалиден")
else:
    start = datetime(day=first_valid_date.day, month=first_valid_date.month, year=first_valid_date.year)
    if first_valid_date_flag:
        print("Первая валидная дата в итервале - " + str(start.date()))

# запрос данных в зависимости от режима
if len(data_from_db) < amount_of_dates:
    if mode == "min_data":
        data = minimizing_data(data_from_db, start, end, n_days, api, db)
        print("Минимизация количества дат в запросах")
    elif mode == "min_req":
        data = minimizing_requests()
        print("Минимизация количества запросов")
    else:
        data = default_getting_data_from_server(data_from_db, start, end, n_days, api, db)
        print("Данные получены с сервера в стандартном режиме")
else:
    data = data_from_db
    print("Данные есть в базе")

plot.make_plot(data)

