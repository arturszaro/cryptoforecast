from django.urls import path
from . import views
from .views import BitcoinChartView, BitcoinListView

urlpatterns = [
    path('', views.index, name='index'),
    path('chart/', BitcoinChartView.as_view()),
    path('tabela/',BitcoinListView.as_view())
]
