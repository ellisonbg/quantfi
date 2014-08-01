import os
import glob
import pandas as pd
import numpy as np

base_dir = os.environ.get('QUANT_QUOTE_DAILY')

def get_symbols():
    """Get a list of all available symbols."""
    files = glob.glob(os.path.join(base_dir,'*'))
    syms = [os.path.splitext(os.path.split(f)[1])[0].split('_')[1] for f in files]
    return syms

def get_file(symbol):
    """Get the absolute filename for a symbols data."""
    symbol = symbol.lower()
    file = 'table_' + symbol + '.csv'
    file = os.path.join(base_dir, file)
    if not os.path.isfile(file):
        raise IOError("File doesn't exist: %r" % file)
    return file

def get_daily_data(symbol):
    """Get a Pandas DataFrame with the daily data for the symbol."""
    f = get_file(symbol)
    df = pd.read_csv(f, header=None, 
                     names=['date','time','open','high','low','close','volume'],
                     parse_dates=[0,],
                     index_col=0)
    return df

def calc_returns(df):
    close = df.close
    prev_close = df.close.shift(1)
    df['r'] = (close - prev_close)/prev_close
    df['lnr'] = np.log(close/prev_close)

_how = {'open':'first', 'high':'max', 'low':'min', 'close':'last', 'volume':'sum'}

def resample(df, period):
    return df.resample(period, closed='right', how=_how, label='right')
