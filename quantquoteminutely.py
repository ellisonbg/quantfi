import os
import glob
import pandas as pd
import numpy as np
import datetime as dt

base_dir = os.environ.get('QUANT_QUOTE_MINUTELY')

def get_symbols():
    """Get a list of all available symbols."""
    files = glob.glob(os.path.join(base_dir,'*'))
    syms = [os.path.splitext(os.path.split(f)[1])[0].split('_')[1] for f in files]
    return syms

def get_file(symbol,date):
    """Get the absolute filename for a symbols data."""
    symbol = symbol.lower()
    file = 'allstocks_' + date + '/table_' + symbol + '.csv'
    file = os.path.join(base_dir, file)
    if not os.path.isfile(file):
        raise IOError("File doesn't exist: %r" % file)
    return file

def get_minutely_data(symbol,start,end):
    data = pd.DataFrame()
    date_range = pd.date_range(start, end, freq='d')
    for date in date_range:
        try:
            date = date.strftime('%Y%m%d')
            f = get_file(symbol,date)
            df = pd.read_csv(f, header=None, 
                             names=['date','time','open','high','low','close','volume', 'splits','earnings','dividends'])
            df.date = pd.to_datetime(df.date, format = '%Y%m%d')

            get_time = lambda x: dt.timedelta(hours=x/100, minutes=(x-(x/100)*100))

            for i in range(len(df.time)):
                df.time.ix[i] = df.date.ix[i] + get_time(df.time.ix[i])

            #shifts from EST to UTC
            df.index = pd.DatetimeIndex(df.time) + dt.timedelta(hours=5)
            df = df.drop('date',axis = 1)
            df = df.drop('time', axis = 1)
            data = pd.concat([data,df],axis = 0)
        except:
            continue
    return data
