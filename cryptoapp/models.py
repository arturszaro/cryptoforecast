from django.db import models
import pandas_datareader as pdr


# Create your models here.
class Bitcoin(models.Model):
    date = models.DateField()
    open = models.FloatField()
    close = models.FloatField()
    ma_30 = models.FloatField(default=0, null=True)
    ma_60 = models.FloatField(default=0, null=True)
    ma_200 = models.FloatField(default=0, null=True)

    def __str__(self):
        return f"{self.date}"

class Predictions(models.Model):
    date = models.DateField()
    close = models.FloatField(default=0)
    prediction = models.FloatField()

    def __str__(self):
        return f"{self.date}"