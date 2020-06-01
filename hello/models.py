from django.db import models

# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=25)
    cLatitude = models.CharField(max_length=25, blank=True, default='')
    cLongitude = models.CharField(max_length=25,blank=True, default='')

    cCountry= models.CharField(max_length=25,blank=True, default='')
    def __str__(self): #show the actual city name on the dashboard
        return self.name

    class Meta: #show the plural of city as cities instead of citys
        verbose_name_plural = 'cities'
class weatherDetail(models.Model):
    #cName = models.CharField(max_length=25)
    iMax = models.DecimalField(max_digits=3, decimal_places=1)
    iMin = models.DecimalField(max_digits=3, decimal_places=1)
    iAvg = models.DecimalField(max_digits=3, decimal_places=1)
    iProbability=models.DecimalField(max_digits=3, decimal_places=1);
    cUnit = models.CharField(max_length=10)
    pass
class weatherAPIForecast (models.Model):
    cName = models.CharField(max_length=25)
    cAdress = models.CharField(max_length=100)
    cKey = models.CharField(max_length=50)
    iCallsPerDay = models.PositiveIntegerField()
    iMaxCallsPerday = models.PositiveIntegerField()
    pass
class weatherDayForecast (models.Model):
    dForecasteDate=models.DateTimeField()
    dCallDate= models.DateTimeField()
    mAPI=models.ForeignKey(weatherAPIForecast, on_delete=models.CASCADE)
    mTemp=models.OneToOneField(weatherDetail, on_delete=models.CASCADE,related_name='tempDetail')
    mRain=models.OneToOneField(weatherDetail, on_delete=models.CASCADE,related_name='rainDetail')
    mHourSun=models.OneToOneField(weatherDetail, on_delete=models.CASCADE,related_name='sunDetail')
    mWind=models.OneToOneField(weatherDetail, on_delete=models.CASCADE,related_name='windDetail')
    cName = models.CharField(max_length=25)
    cIcon = models.CharField(max_length=25)

##########################
