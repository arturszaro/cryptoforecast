from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from .models import *
import pandas as pd
from datetime import date
from .tasks import ad_test, get_data, deletedata


def index(request):
    today = date.today()
    datarange = f'{date(today.year - 3, today.month, today.day)}' # 3 lata wstecz
    dataset = 'BTC-USD' # Bitcoin USD
    get_data(dataset, datarange) # Zapisz dane w bazie danych
    ad_test()
    item = Bitcoin.objects.all().values().order_by('date')
    df = pd.DataFrame(item)

    # deletedata(df.id) #usuwa wszystkie dane z bazy Bitcoin

    mydict = {
        'df': df.to_html(classes='table table-dark table-hover')
    } # tablica z DataFrame na pierwszej stronie

    return render(request, 'index.html', context=mydict)


class BitcoinChartView(TemplateView):
    template_name = "chart.html"

    def get_context_data(self, **kwargs):
        today = date.today()
        context = super().get_context_data(**kwargs)
        context["qs"] = Bitcoin.objects.all().filter(
            date__range=[f"{date(today.year - 2, today.month, today.day)}", f"{today}"]).order_by('date')
        context["qs2"] = Predictions.objects.all()
        return context


class BitcoinListView(ListView):
    # draw('BTC-USD', '2022-05-01')
    model = Bitcoin
    template_name = "tabela.html"

    def get_queryset(self):
        return Bitcoin.objects.order_by('date')
