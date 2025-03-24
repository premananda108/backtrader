import backtrader as bt
import yfinance as yf
import os  # Import the os module

# --- Data Download and Preparation ---
data_folder = 'data'  # Define a folder to store your data
if not os.path.exists(data_folder):
    os.makedirs(data_folder)  # Create the folder if it doesn't exist

tsla_dataname = os.path.join(data_folder, 'tsla.csv')  # Full path to the CSV file
start_date = '2021-01-01'
end_date = '2021-12-31'

# Check if the file already exists
if os.path.exists(tsla_dataname):
    print(f"Loading data from {tsla_dataname}")
    # Option 1: Use GenericCSVData (since we have a CSV)
    tsla_daily_parsed = bt.feeds.GenericCSVData(dataname=tsla_dataname,
                                                datetime=0,
                                                open=1,
                                                high=2,
                                                low=3,
                                                close=4,
                                                volume=5,
                                                openinterest=None,
                                                fromdate=bt.datetime.datetime.strptime(start_date, '%Y-%m-%d'),
                                                todate=bt.datetime.datetime.strptime(end_date, '%Y-%m-%d'))

    # Option 2: Load into Pandas, then use PandasData (still good)
    # tsla_daily = pd.read_csv(tsla_dataname, index_col='Date', parse_dates=True)
    # tsla_daily_parsed = bt.feeds.PandasData(dataname=tsla_daily,
    #                                         fromdate=bt.datetime.datetime.strptime(start_date, '%Y-%m-%d'),
    #                                         todate=bt.datetime.datetime.strptime(end_date, '%Y-%m-%d'))
else:
    print(f"Downloading data and saving to {tsla_dataname}")
    tsla_daily = yf.download('TSLA', start=start_date, end=end_date)
    # Flatten the MultiIndex *before* saving
    tsla_daily.columns = tsla_daily.columns.get_level_values(0)
    tsla_daily.to_csv(tsla_dataname)

    # Now load it (same options as above - GenericCSVData or PandasData)
    tsla_daily_parsed = bt.feeds.GenericCSVData(dataname=tsla_dataname,
                                                datetime=0,
                                                open=1,
                                                high=2,
                                                low=3,
                                                close=4,
                                                volume=5,
                                                openinterest=None,
                                                fromdate=bt.datetime.datetime.strptime(start_date, '%Y-%m-%d'),
                                                todate=bt.datetime.datetime.strptime(end_date, '%Y-%m-%d'),
                                                dtformat='%Y-%m-%d')


# --- Strategy Definition ---
class MyStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def next(self):
        self.log(f'Close, {self.dataclose[0]}')
        if self.dataclose[0] < self.dataclose[-1]:
            self.log(f'BUY CREATE, {self.dataclose[0]}')
            self.buy()

# --- Cerebro Engine Setup and Execution ---
cerebro = bt.Cerebro()
cerebro.adddata(tsla_daily_parsed)
cerebro.addstrategy(MyStrategy)
cerebro.broker.setcash(100000.0)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot(iplot=False)