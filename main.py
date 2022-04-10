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

args = parser.parse_args()

db = DataStorage("btc_tracker")
api = BTCApi()
plot = plotData()

start_date = args.start_date
end_date = args.end_date
n_days = timedelta(args.n)

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
