import os
import glob
import pandas as pd
import numpy as np
import datetime as dt

base_dir = os.environ.get('QUANT_QUOTE_MINUTELY')

def get_symbols():
    """Get a list of all available symbols."""
    files = glob.glob(os.path.join(base_dir,'*'))
    syms = []
    for f in files:
        lst = os.listdir(f)
        for csv in lst:
            sym = csv.replace('.csv','').split('_')[1]
            if sym not in syms:
                syms.append(sym)
    return syms

def get_file(symbol,date):
    """Get the absolute filename for a symbols data."""
    symbol = symbol.lower()
    file = 'allstocks_' + date + '/table_' + symbol + '.csv'
    file = os.path.join(base_dir, file)
    if not os.path.isfile(file):
        raise IOError("File doesn't exist: %r" % file)
    return file

def get_start():
    return glob.glob(os.path.join(base_dir,'*'))[0].split('_')[-1]

def get_end():
    return glob.glob(os.path.join(base_dir,'*'))[-1].split('_')[-1]

def _parse_datetime(date,time):
    get_time = lambda x: dt.time(hour=int(x)/100, minute=(int(x)-(int(x)/100)*100))
    parse = lambda x,y: dt.datetime.combine(dt.datetime.strptime(x,'%Y%m%d'), get_time(y))
    return parse(date,time)

def get_minutely_data(symbol, start=None, end=None):
    """Get stock data from QuantQuote dataset for symbol and date range"""
    if start is None:
        start = get_start()
    if end is None:
        end = get_end()
    data = []
    date_range = pd.date_range(start, end, freq='d')
    for date in date_range:
        try:
            date = date.strftime('%Y%m%d')
            f = get_file(symbol,date)
            df = pd.read_csv(f, header=None,
                             names=['date','time','open','high','low','close','volume',
                                    'splits','earnings','dividends'], index_col = 0,
                             parse_dates = [[0,1]], date_parser = _parse_datetime)
            
            #shifts from EST to UTC. What about EDT?
            df.index = df.index + dt.timedelta(hours=5)
            data.append(df)
        except IOError:#, AttributeError):#, NameError:
            continue
    data = pd.concat(data, axis = 0)
    data.index.name = None
    return data

_how = {'open':'first', 'high':'max', 'low':'min', 'close':'last', 'volume':'sum', 'splits':'last',
    'earnings':'first', 'dividends':'sum'}

def resample(df, period):
    df = df.resample(period, closed='right', how=_how, label='right')
    return df[['open','high','low','close','volume', 'splits','earnings','dividends']]

def log_returns(data,period):
    return np.log(data.close/data.close.shift(period))

