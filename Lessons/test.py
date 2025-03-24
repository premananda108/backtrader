import yfinance as yf
import mplfinance as mpf  # Install with: pip install mplfinance
import pandas as pd

# --- Data Download (Minimal) ---
start_date = '2023-01-01'
end_date = '2023-01-15'
tsla_daily = yf.download('TSLA', start=start_date, end=end_date)
tsla_daily.columns = tsla_daily.columns.get_level_values(0)
tsla_daily = tsla_daily.asfreq('B')

# --- Plot with mplfinance ---
mpf.plot(tsla_daily, type='candle', style='yahoo', volume=True)

print(tsla_daily.index)
print(tsla_daily.index.dtype)