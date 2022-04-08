from API import BTCApi
from DB import DataStorage
from Plot import plotData
from datetime import datetime




db = DataStorage("btc_tracker")
api = BTCApi()
start_date = input()
end_date = input()
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
    data = api.make_request(start_date, end_date)
    print("Данные получены с сервера")
    db.load_to_database(data)

else:
    data = db.get_from_database(start_date, end_date)
    print("Данные есть в базе")

print(data)

