from celery import shared_task
from celery.schedules import crontab
from .models import *
import numpy as np
import pandas as pd

#TODO:
# Periodic tasks (Celery/redis) - Taski wykonują się same w tle nie przed każdym włączeniem strony
# Poprawa modelu / wyników (Keras / Pandas)
# Praca nad wizualizacją danych (chart.js && Dash?)
# Praca nad układem oraz wyglądem strony (templates / CSS)
# Nazewniztwo danych, modeli, zmiennych oraz poprawa czytelności kodu (Python, Django)
# Dodać API do pobierania danych oraz do zmiany parametrów kalkulacji (Django Rest Framework)
# Dodać wskaźnik z dokładnością dotychczasowych przewidywań (NumPy,Pandas)
from datetime import date

today = date.today()
datarange = f'{date(today.year - 3, today.month, today.day)}'  # 3 lata wstecz


@shared_task(name='get_data_task', bind=True)  # co 3 godziny
def get_data(self, x='META', y=datarange):
    df = pdr.get_data_yahoo(x, y) #Pobieranie danych datarange oraz waluta btc uscd
    df['Date'] = df.index
    df['MA_30'] = df['Close'].rolling(30).mean()
    df['MA_60'] = df['Close'].rolling(60).mean()
    df['MA_200'] = df['Close'].rolling(200).mean()
    rows = df.shape[0]
    for r in range(0, rows):
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


@shared_task(bind = True)
def deletedata(self, database):
    database.objects.all().delete()


@shared_task(bind = True, name='Prediction')
def ad_test(self):
    deletedata(Predictions)
    #Settings:
    #Ile dni wstecz do treningu
    d_range = 60
    #Jaki procent do treningu a jaki do testu
    split_percentage = 0.5
    #Ile dni wstecz do prognozy danych
    n_input= 7
    #ile dni wyliczyć forecast
    x_input = 14
    #liczba epoch
    e_input = 15

    # 1. Pobranie danych
    df = pd.DataFrame(data=list(zip([Bitcoin.objects.all()[i].date for i in range(Bitcoin.objects.all().count())]
                                    ,[Bitcoin.objects.all()[i].close for i in range(Bitcoin.objects.all().count())])),
                      columns=['Date','Close'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Close'] = pd.to_numeric(df['Close'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    df = df[-d_range:] # liczba dni pobranych do analizy

    #2. Przygotowanie danych do modelu
    split = int(len(df) * split_percentage)
    train = df.iloc[:split]
    test = df.iloc[split:]

    from sklearn.preprocessing import MinMaxScaler

    scaler = MinMaxScaler()
    scaler.fit(train)
    scaled_train = scaler.transform(train)
    scaled_test = scaler.transform(test)


    from keras.preprocessing.sequence import TimeseriesGenerator
    n_features = 1
    generator = TimeseriesGenerator(scaled_train, scaled_train, length=n_input, batch_size=1)
    X, y = generator[0]

    # 3. Trening modelu
    from keras.models import Sequential
    from keras.layers import Dense
    from keras.layers import LSTM

    model = Sequential()
    model.add(LSTM(100, activation='relu', input_shape=(n_input, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(generator, epochs=e_input)

    #4.Forecasting
    test_predictions = []
    first_eval_batch = scaled_train[-n_input:]
    current_batch = first_eval_batch.reshape((1, n_input, n_features))

    for i in range(len(test)+x_input):
        #make prediction value for the first batch
        current_pred = model.predict(current_batch)[0]
        #append prediction into the array
        test_predictions.append(current_pred)
        #use the prediction to update batch and remove first value
        current_batch = np.append(current_batch[:, 1:, :], [[current_pred]], axis=1)

    #dodanie 3 pustych dat by móc przypisać 3 dodatkowe predykcje
    from datetime import date

    today = date.today()
    new = []
    for x in range(1,x_input+1):

        new.append([date(today.year, today.month, today.day+x),test.Close[[-1]]])
    future_days = pd.DataFrame(data=new,columns=['Date','Close'])
    future_days.set_index('Date',inplace=True)
    test = pd.concat([test,future_days])
    true_predictions = scaler.inverse_transform(test_predictions)
    pd.options.mode.chained_assignment = None
    test['Predictions'] = true_predictions

    #5.Zapis w bazie danych
    test['Date'] = test.index
    rows = test.shape[0]
    for r in range(0, rows):
        p = Predictions(
             date=test.Date[r],
            prediction=test.Predictions[r],
            close= test.Close[r]
        )
        p.save()