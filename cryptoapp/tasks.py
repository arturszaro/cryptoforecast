from celery import shared_task
import pandas as pd
import pandas_datareader as pdr
from datetime import date,datetime
from pmdarima import auto_arima
import warnings
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import matplotlib
from .models import *

@shared_task(bind=True)
def go_to_sleep(x,y):
    df = pdr.get_data_yahoo(x,y) #pobiera dane z yahoo od 01.05

    return 'Done'



@shared_task(bind=True)
def get_data(self, x,y):
    df = pdr.get_data_yahoo(x, y)  # pobiera dane z yahoo od 01.05
    df['Date'] = df.index
    df['MA_30'] = df['Close'].rolling(30).mean()
    df['MA_60'] = df['Close'].rolling(60).mean()
    df['MA_200'] = df['Close'].rolling(200).mean()
    rows = df.shape[0]
    for r in range(0,rows):
        if not Bitcoin.objects.filter(date=df.Date[r]):
            b = Bitcoin(
                date=df.Date[r],
                open=df.Open[r],
                close=df.Close[r],
                ma_30=df.MA_30[r],
                ma_60=df.MA_60[r],
                ma_200=df.MA_200[r],
            )
            b.save()

    return 'Done'

@shared_task(bind=True)
def deletedata(self, id):
    rows = Bitcoin.objects.all().count()
    for r in range(0,rows+id): #rows+id najnowszego wiersza aby usunąć wszystko
        Bitcoin.objects.filter(id=r).delete()
    return 'Done'

@shared_task(bind=True)
def ad_test(self,x,y):
    today =datetime.today()
    df = pdr.get_data_yahoo(x, y)
    df = df.dropna()
    dftest = adfuller(df['Close'],autolag = "AIC")
    print("1. ADF: ", dftest[0])
    print("2. P-Value: ", dftest[1])
    print("1. Num of Lags: ", dftest[2])
    print("1. Num of Observations Used for ADF Regression and Critical Values Calculation: ", dftest[3])
    print("1. Critical Values: ")
    for key, val in dftest[4].items():
        print(f"/t{key}: {val}")

    warnings.filterwarnings('ignore')
    stepwise_fit = auto_arima((df['Close']), trace=True, suppress_warnings=True)
    stepwise_fit.summary()
    model = ARIMA(df['Close'],order=(0,1,0))
    model = model.fit()
    model.summary()
    pred = model.predict(start=len(df), end=len(df)+1,typ='levels').rename('ARIMA Predictions')
    print(pred)
