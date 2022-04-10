import matplotlib.pyplot as plt


class plotData:

    def make_plot(self, data: dict):

        dates = []
        prices = []
        for date, price in data.items():
            date = int(date.replace('-', ''))
            price = float(price)
            dates.append(date)
            prices.append(price)

        plt.plot(prices)
        plt.show()

