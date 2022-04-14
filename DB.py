import sqlite3


class DataStorage:
    data_base_name = None
    connection = None
    cursor = None

    def __init__(self, data_base_name: str):
        self.data_base_name = data_base_name
        self.connection = sqlite3.connect(data_base_name)
        self.cursor = self.connection.cursor()
        self._create_database()

    def _create_database(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS btc_data(
        date TEXT,
        value TEXT,
        UNIQUE(date));
        """)
        self.connection.commit()

    def load_to_database(self, data: dict):
        for date, value in data.items():
            self.cursor.execute("INSERT OR IGNORE INTO btc_data(date, value) VALUES (?, ?)",
                                (date, value)
                                )
        self.connection.commit()

    def get_from_database(self, start, end):
        self.cursor.execute("SELECT * FROM btc_data where date >= \'%s\' and date <= \'%s\' ORDER BY date"
                            % (start, end)
                            )
        raw_data = self.cursor.fetchall()
        data = {}
        for i in raw_data:
            data[i[0]] = i[1]
        return data
