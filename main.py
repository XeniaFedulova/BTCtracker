from API import BTCApi
from DB import DataStorage
from Plot import plotData
from datetime import datetime
from datetime import timedelta
import argparse

def make_date_of_string(date:str):
    dates = {}
    dates['year'], dates['month'], dates['day'] = date.split('-')
    for key, item in dates.items():
        if item.startswith("0"):
            item = item.replace("0", "")
        dates[key] = int(item)
    date = datetime(day=dates['day'], month=dates['month'], year=dates['year'])
    return date

def search_first_valid_date(db: DataStorage, api: BTCApi, start, end):
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

#парсинг аргументов из командной строки
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-start_date', type=str, help='input start date in format yyyy-mm-dd')
parser.add_argument('-end_date', type=str, help='input end date in format yyyy-mm-dd')
parser.add_argument('-n', type=int, help='input maximum amount of days in one request, n <= 100')
parser.add_argument('-first_valid_date', type=int, help='finds first valid date in the interval')
parser.add_argument('-min_data', type=int, help='minimizes amount of requested data')
parser.add_argument('-min_req', type=int, help='minimizes amount of requests')

args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date
n_days = timedelta(args.n)
first_valid_date = args.first_valid_date

#объявление объектов классов
db = DataStorage("btc_tracker")
api = BTCApi()
plot = plotData()


start = make_date_of_string(start_date)
end = make_date_of_string(end_date)
time = end - start
amount_of_dates = time.days
data_from_db = db.get_from_database(start_date, end_date)


first_valid_date = search_first_valid_date(db, api, start, end)

if first_valid_date == None:
    print("Заданный интервал невалиден")
else:
    start = datetime(day=first_valid_date.day, month=first_valid_date.month, year=first_valid_date.year)
    print("Первая валидная дата в итервале - " + str(start.date()))


if len(data_from_db) < amount_of_dates:
    start_date_req = start

    while True:
        end_date_req = start_date_req + n_days

        if end_date_req >= end:
            end_date_req = end
            data = api.make_request(str(start_date_req.date()), str(end_date_req.date()))
            print("making request")
            db.load_to_database(data)
            break

        print("making request")
        data = api.make_request(str(start_date_req.date()), str(end_date_req.date()))
        print(data)
        start_date_req = end_date_req
        db.load_to_database(data)

    print("Данные получены с сервера")

else:
    print("Данные есть в базе")

raw_data = db.get_from_database(start_date, end_date)
data = {}
for i in raw_data:
    data[i[0]] = i[1]

plot.make_plot(data)
