from API import BTCApi
from DB import DataStorage
from Plot import plotData
from datetime import datetime
from datetime import timedelta
import argparse

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

db = DataStorage("btc_tracker")
api = BTCApi()
plot = plotData()

dates = {}
dates['start_year'], dates['start_month'], dates['start_day'] = start_date.split('-')
dates['end_year'], dates['end_month'], dates['end_day'] = end_date.split('-')

for key, item in dates.items():
    if item.startswith("0"):
        item = item.replace("0", "")
    dates[key] = int(item)

start = datetime(day=dates['start_day'], month=dates['start_month'], year=dates['start_year'])
end = datetime(day=dates['end_day'], month=dates['end_month'], year=dates['end_year'])
time = end - start
amount_of_dates = time.days
data_from_db = db.get_from_database(start_date, end_date)


def search_first_valid_date(db: DataStorage, api:BTCApi, start, end):
    data = db.get_from_database(start.date(), start.date())
    if len(data) != 0:
        data = data[0][0]
        print("Первая валидная дата из интервала - "+data)
        return data
    else:
        try:
            data = api.make_request(start.date(), start.date())
            i = input()
            data = list(data.keys())[0]
            print("Первая валидная дата из интервала - "+data)
            return data
        except:
            while True:
                print("Бинарный поиск")
                delta = (end - start) / 2
                start += delta
                print(start)
                while True:
                    data = db.get_from_database(start.date(), start.date())
                    if len(data) == 0:
                        try:
                            data = api.make_request(str(start.date()), str(start.date()))
                            end = start
                            start -= delta
                            delta = (end - start) / 2
                            start = start + delta
                            print(start)
                            print(end)
                            i = input()
                            #поиск в меньшей половине
                        except:
                            delta = (end - start) / 2
                            start += delta
                            print(start)
                            i = input()
                            #поиск в большей половине
                    else:
                        delta = (end - start) / 2
                        start += delta
                        print(start)
                        i = input()
                        #поиск в большей половине




print(search_first_valid_date(db, api, start, end))
i = input()




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
