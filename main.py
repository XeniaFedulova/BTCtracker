from requests.compat import JSONDecodeError

from API import BTCApi
from DB import DataStorage
from Plot import plotData
from datetime import datetime
from datetime import timedelta
import argparse


def make_date_of_string(date: str):
    date = datetime.strptime(date, '%Y-%m-%d')
    return date


def sort_dates_by_order(dates: dict):
    sorted_dates = sorted(dates.keys())
    sorted_dict = {}

    for date in sorted_dates:
        sorted_dict[date] = dates[date]

    return sorted_dict


def search_first_valid_date(api: BTCApi, start, end):
    try:
        api.make_request(str(start.date()), str(start.date()))
        return start
    except:
        # JSONDecodeErrordeError as e
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
                # поиск в меньшей половине
            except:
                delta = (end - start) / 2
                start += delta
                # поиск в большей половине


def default_getting_data(data_from_db: dict, start: datetime, end: datetime, n_days: timedelta,
                         api: BTCApi):
    start_req_date = start
    end_req_date = start_req_date + n_days
    curr_date = start_req_date
    one_day = timedelta(days=1)

    while start_req_date < end:

        if end_req_date >= end:
            end_req_date = end

        while curr_date <= end_req_date:
            if str(curr_date.date()) not in data_from_db:
                api.put_req_data_to_dict(data_from_db, str(start_req_date.date()), str(end_req_date.date()))
                break
            curr_date += one_day

        start_req_date = end_req_date
        end_req_date = start_req_date + n_days


    sorted_data = sort_dates_by_order(data_from_db)
    return sorted_data


def minimizing_data(data_from_db: dict, start: datetime, end: datetime, n_days: timedelta, api: BTCApi):
    one_day = timedelta(days=1)
    curr_date = start
    counter = 0
    start_req_date = curr_date
    while True:
        if str(curr_date.date()) not in data_from_db:
            if curr_date == end:
                api.put_req_data_to_dict(data_from_db, str(start_req_date.date()), str((curr_date).date()))
                break
            if counter == 0:
                start_req_date = curr_date
                counter += 1
            elif counter == n_days.days - 1:
                api.put_req_data_to_dict(data_from_db, str(start_req_date.date()), str((curr_date).date()))
                counter = 0
            else:
                counter += 1
        else:
            if counter != 0:
                end_req_date = curr_date - one_day
                api.put_req_data_to_dict(data_from_db, str(start_req_date.date()), str((end_req_date).date()))
            if curr_date == end:
                break
            counter = 0

        curr_date += one_day

    sorted_data = sort_dates_by_order(data_from_db)
    return sorted_data


def minimizing_requests(data_from_db: dict, start: datetime, end: datetime, n_days: timedelta, api: BTCApi):
    one_day = timedelta(days=1)
    start_req_date = start
    end_req_date = start_req_date + n_days
    start_this_req_date = start_req_date
    end_this_req_date = end_req_date

    while start_req_date < end:

        if end_req_date > end:
            end_req_date = end + one_day

        curr_date = start_req_date
        while curr_date <= end_req_date:
            if str(curr_date.date()) in data_from_db:
                if curr_date == end_req_date:
                    break
                curr_date += one_day
            else:
                start_this_req_date = curr_date
                break

        if curr_date == end_req_date:
            start_req_date += n_days
            end_req_date += n_days
            continue

        curr_date = end_req_date - one_day
        while curr_date > start_this_req_date:
            if str(curr_date.date()) in data_from_db:
                curr_date -= one_day
            else:
                end_this_req_date = curr_date

                break

        api.put_req_data_to_dict(data_from_db, str(start_this_req_date.date()), str(end_this_req_date.date()))
        start_req_date += n_days
        end_req_date += n_days

    sorted_data = sort_dates_by_order(data_from_db)
    return sorted_data


if __name__ == '__main__':

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
    one_day = timedelta(days=1)
    end = make_date_of_string(end_date) - one_day
    end_date = str(end.date())
    time = end - start
    amount_of_dates = time.days
    data_from_db = db.get_from_database(start_date, end_date)
    length = len(data_from_db)

    # поиск первой валидной даты
    first_valid_date = search_first_valid_date(api, start, end)
    if first_valid_date == None:
        print("Заданный интервал невалиден")
    else:
        start = datetime(day=first_valid_date.day, month=first_valid_date.month, year=first_valid_date.year)
        if first_valid_date_flag:
            print("Первая валидная дата в итервале - " + str(start.date()))

    # запрос данных в зависимости от режима
    print("Количество дат в кэше по заданному интервалу: " + str(length))
    print(data_from_db)
    if len(data_from_db) < amount_of_dates:
        print("Недостаточно данных из кэша, запрос данных с сервера")
        if mode == "min_data":
            data = minimizing_data(data_from_db, start, end, n_days, api)
            db.load_to_database(data)
            print("Минимизация количества дат в запросах")
        elif mode == "min_req":
            data = minimizing_requests(data_from_db, start, end, n_days, api)
            db.load_to_database(data)
            print("Минимизация количества запросов")
        else:
            data = default_getting_data(data_from_db, start, end, n_days, api)
            db.load_to_database(data)
            print("Данные получены с сервера в стандартном режиме")
    else:
        data = data_from_db
        print("Данные получены из кэша")

    plot.make_plot(data)
