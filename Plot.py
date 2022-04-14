import matplotlib.pyplot as plt


class plotData:

    def make_plot(self, data: dict):
        dates = []
        prices = []
        for date, price in data.items():
            price = float(price)
            dates.append(date)
            prices.append(price)

        length = len(dates)
        if length < 10:
            offset = 1
        else:
            offset = int(length / 10)

        plt.plot(dates, prices)
        plt.title("Курс BTC")
        plt.xlabel("Дата")
        plt.ylabel("Цена, $")
        plt.xticks(dates[::offset], rotation="vertical")

        plt.show()
