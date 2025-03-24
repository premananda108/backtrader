import backtrader as bt
import yfinance as yf
import os
import ephem
import datetime
import matplotlib.pyplot as plt  # Import matplotlib
import pandas as pd

# ... (rest of your code: data loading, strategy, cerebro setup) ...
class LunarCycleStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None  # To keep track of pending orders
        self.moon = ephem.Moon()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        self.log(f'Close, {self.dataclose[0]}')

        # Get today's and previous day's dates
        today = self.datas[0].datetime.date(0)
        previous_day = self.datas[0].datetime.date(-1)

        # Calculate moon phase for today and previous day
        self.moon.compute(today)
        today_phase = self.moon.moon_phase
        self.moon.compute(previous_day)
        previous_day_phase = self.moon.moon_phase

        # Check if we are already in a position
        if self.position:
            # Sell at the end of the waning moon (phase goes from full to new)
            if (previous_day_phase > 0.5 and today_phase < 0.5 and
                    self.dataclose[-1] > self.dataclose[0]):
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell()  # Sell all shares

        else:  # Not in a position
            # Buy at the beginning of the waxing moon (phase goes from new to full)
            if (previous_day_phase > today_phase and today_phase <0.5 and
                    self.dataclose[0] > self.dataclose[-1]):
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                self.order = self.buy()

# --- Data Download and Preparation ---
data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

tsla_dataname = os.path.join(data_folder, 'tsla.parquet')
start_date = '2021-01-01'
end_date = '2023-12-31'  # Extended date range for more lunar cycles

if os.path.exists(tsla_dataname):
    print(f"Loading data from {tsla_dataname}")
    tsla_daily = pd.read_parquet(tsla_dataname)
    tsla_daily_parsed = bt.feeds.PandasData(dataname=tsla_daily,
                                            fromdate=datetime.datetime.strptime(start_date, '%Y-%m-%d'),
                                            todate=datetime.datetime.strptime(end_date, '%Y-%m-%d'))
else:
    print(f"Downloading data and saving to {tsla_dataname}")
    tsla_daily = yf.download('TSLA', start=start_date, end=end_date)
    tsla_daily.columns = tsla_daily.columns.get_level_values(0)
    tsla_daily.to_parquet(tsla_dataname)
    tsla_daily_parsed = bt.feeds.PandasData(dataname=tsla_daily,
                                            fromdate=datetime.datetime.strptime(start_date, '%Y-%m-%d'),
                                            todate=datetime.datetime.strptime(end_date, '%Y-%m-%d'))

# --- Cerebro Engine Setup and Execution ---
cerebro = bt.Cerebro()
cerebro.adddata(tsla_daily_parsed)
cerebro.addstrategy(LunarCycleStrategy)
cerebro.broker.setcash(100000.0)
cerebro.addsizer(bt.sizers.PercentSizer, percents=95) # invest 95%

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


plot = cerebro.plot(iplot=False)[0][0]  # Get the Matplotlib figure
plt.rcParams['figure.figsize'] = [18, 10]
plt.rcParams.update({'font.size': 12})
plot.autofmt_xdate()  # Rotate date labels
plt.show()  # Explicitly show the plot