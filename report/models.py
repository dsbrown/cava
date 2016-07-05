from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Make(models.Model):
    name        = models.CharField(max_length=128)
    niceName    = models.CharField(max_length=128)
    edmunds_id  = models.IntegerField(default=0, blank=True)

    def get_absolute_url(self):
        return reverse('make-detail', kwargs={'pk': self.pk})

    def __unicode__(self):
        return u'%s' % (self.name)


class MakeAlias(models.Model):
    alias       = models.CharField(max_length=128)
    make        = models.ForeignKey('Make')

class Model(models.Model):
    name        = models.CharField(max_length=128)
    niceName    = models.CharField(max_length=128)
    make        = models.ForeignKey('Make')
    year        = models.IntegerField()                                                         # CL years 2017 - 1900
    related     = models.ManyToManyField('Model', blank=True)
    edmunds_id  = models.CharField(max_length=128, default="", blank=True)
    edmunds_year_id        = models.IntegerField(default=0, blank=True)
    avg_price              = models.DecimalField(max_digits=11, decimal_places=2, default=0, blank=True) 
    avg_condition          = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)
    avg_location_latitude  = models.DecimalField(max_digits=10, decimal_places=6, default=0, blank=True)
    avg_location_longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0, blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.year,self.name)

class Trim(models.Model):
    niceName    = models.CharField(max_length=128,default="", blank=True)     # this may not be necessary
    trim        = models.CharField(max_length=128,default="", blank=True)    
    model       = models.ForeignKey('Model',default=None, null=True)

class ModelAlias(models.Model):
    niceName    = models.CharField(max_length=128,default="", blank=True)     
    alias       = models.CharField(max_length=128,default="", blank=True)

class ClPost(models.Model):
    TITLE_CLEAN       = 'CL'
    TITLE_SALVAGE     = 'SA'
    TITLE_REBUILT     = 'RE'
    TITLE_PARTS_ONLY  = 'PA'
    TITLE_LIEN        = 'LE'
    TITLE_MISSING     = 'MS'

    TITLE_STATUS = (
        (TITLE_CLEAN,     'Clean'),
        (TITLE_SALVAGE,   'Salvage'),
        (TITLE_REBUILT,   'Rebuilt'),
        (TITLE_PARTS_ONLY,'Parts Only'),
        (TITLE_LIEN,      'Lien'),
        (TITLE_MISSING,   'Missing'),
    )

    COMPACT     = 'CP'
    FULL        = 'FU'
    MIDSIZE     = 'MS'
    SUBCOMPACT  = 'SC'

    VEHICLE_SIZE = (
        (COMPACT,   'Compact'),
        (FULL,      'Full'),
        (MIDSIZE,   'Mid Size'),
        (SUBCOMPACT,'Sub Compact'),
    )

    GAS         = 'GA'
    DIESEL      = 'DS'
    HYBRID      = 'HY'
    ELECTRIC    = 'EL'
    FUELOTHER   = 'OT'

    FUEL_CHOICES = (
        (GAS,       'Gas'),
        (DIESEL,    'Diesel'),
        (HYBRID,    'Hybrid'),
        (ELECTRIC,  'Electric'),
        (FUELOTHER, 'Fuel Other'),
    )

    BUS         = 'BS'
    CONVERTIBLE = 'CV'
    COUPE       = 'CP'
    HATCHBACK   = 'HB'
    MINIVAN     = 'MV'
    OFFROAD     = 'OR'
    PICKUP      = 'PU'
    SEDAN       = 'SD'
    TRUCK       = 'TK'
    SUV         = 'SU'
    WAGON       = 'WG'    

    VEHICLE_TYPE = (
        (BUS,           'Bus'),
        (CONVERTIBLE,   'Convertible'),
        (COUPE,         'Coupe'),
        (HATCHBACK,     'Hatchback'),
        (MINIVAN,       'Mini Van'),
        (OFFROAD,       'Offroad'),
        (PICKUP,        'Pickup'),
        (SEDAN,         'Sedan'),
        (TRUCK,         'Truck'),
        (SUV,           'SUV'),
        (WAGON,         'Wagon'),        
    )

    CONDITION_NEW        = 'NE'
    CONDITION_LIKE_NEW   = 'LN'
    CONDITION_EXCELLENT  = 'EX'
    CONDITION_GOOD       = 'GD'
    CONDITION_FAIR       = 'FA'
    CONDITION_SALVAGE    = 'SA'

    CONDITION = (
        (CONDITION_NEW,         'New'),
        (CONDITION_LIKE_NEW,    'Like New'),
        (CONDITION_EXCELLENT,   'Excellent'),
        (CONDITION_GOOD,        'Good'),
        (CONDITION_FAIR,        'Fair'),
        (CONDITION_SALVAGE,     'Salvage'),
    )

    CYLINDERS_3         = 3
    CYLINDERS_4         = 4
    CYLINDERS_5         = 5
    CYLINDERS_6         = 6
    CYLINDERS_8         = 8
    CYLINDERS_10        = 10
    CYLINDERS_12        = 12
    CYLINDERS_OTHER     = 99

    CYLINDERS = (
        (CYLINDERS_3,   '3 Cylinders'),
        (CYLINDERS_4,   '4 Cylinders'),
        (CYLINDERS_5,   '5 Cylinders'),
        (CYLINDERS_6,   '6 Cylinders'),
        (CYLINDERS_8,   '8 Cylinders'),
        (CYLINDERS_10,  '10 Cylinders'),
        (CYLINDERS_12,  '12 Cylinders'),
        (CYLINDERS_OTHER,'Other Cylinders'),
    )

    MANUAL          = 'MA'
    AUTOMATIC       = 'AU'
    OTHER           = 'OT'

    TRANSMISSION = (
        (MANUAL,   'Manual'),
        (AUTOMATIC,'Automatic'),
        (OTHER,    'Other'),
    )

    FWD         = 'FD'
    RWD         = 'RD'
    FOURWD      = 'FW'

    DRIVE = (
        (FWD,   'Front Wheel Drive'),
        (RWD,   'Rear Wheel Drive'),
        (FOURWD,'Four Wheel Drive'),
    )

    BLACK       = 'BL'
    BLUE        = 'BU'
    GREEN       = 'GN'
    GREY        = 'GY'
    ORANGE      = 'OR'
    PURPLE      = 'PU'
    RED         = 'RD'
    SILVER      = 'SL'
    WHITE       = 'WH'
    YELLOW      = 'YL'
    CUSTOM      = 'CU'
    BROWN       = 'BR'

    PAINT_COLOR = (
        (BLACK, 'Black'),
        (BLUE,  'Blue'),
        (GREEN, 'Green'),
        (GREY,  'Grey'),
        (ORANGE,'Orange'),
        (PURPLE,'Purple'),
        (RED,   'Red'),
        (SILVER,'Silver'),
        (WHITE, 'White'),
        (YELLOW,'Yellow'),
        (CUSTOM,'Custom'),
        (BROWN, 'Brown'),
    )

    cl_main_title   = models.CharField(max_length=1024, default=0, blank=True)                    # cl_main_title   # i.e 2008 Mazda RX-8 40TH Anniversary Addition
    detail_title    = models.CharField(max_length=1024, default=0, blank=True)                    # detail_titlei.e: 2008 Mazda RX-8 40TH Anniversary Addition
    title_status    = models.CharField(max_length=2,choices=TITLE_STATUS, default="", blank=True) # title of ownership status possible values: clean, salvage, rebuilt, parts only, lien, missing 
    v_size          = models.CharField(max_length=2,choices=VEHICLE_SIZE, default="", blank=True) # compact full mid-size sub-compact    
    fuel            = models.CharField(max_length=2,choices=FUEL_CHOICES, default="", blank=True) # gas, diesel, hybrid, electric, other     
    v_type          = models.CharField(max_length=2,choices=VEHICLE_TYPE, default="", blank=True) # bus convertible coupe, hatchback, mini-van, offroad, pickup, sedan, truck, SUV, wagon, van, other
    condition       = models.CharField(max_length=2,choices=CONDITION, default="", blank=True)    # new, like new, excellent, good, fair, salvage    
    cylinders       = models.IntegerField(choices=CYLINDERS,default=0)                            # 3,4,5,6,8,10,12,Other  cylinders
    transmission    = models.CharField(max_length=2,choices=TRANSMISSION, default="", blank=True) # manual, automatic, other 
    drive           = models.CharField(max_length=2,choices=DRIVE, default="", blank=True)        # fwd, rwd, 4wd
    odometer        = models.IntegerField(default=0, blank=True)                                  # i.e 28000    
    paint_color     = models.CharField(max_length=2,choices=PAINT_COLOR, default="", blank=True)  # black, blue, green, grey, orange, purple, red, silver, white, yellow,custom,brown
    map_latitude    = models.DecimalField(max_digits=10, decimal_places=6, default=0, blank=True) # 47.617400
    map_longitude   = models.DecimalField(max_digits=10, decimal_places=6, default=0, blank=True) # -122.142600
    map_link        = models.URLField(max_length=1024, blank=True, null=True)                     # https://maps.google.com/maps/preview/@47.617400,-122.142600,16z
    map_accuracy    = models.IntegerField(default=0, blank=True)                                  # 0 ...nn
    address         = models.CharField(max_length=256, default=0, blank=True)                     # rarely provided but sometimes ...
    pri_image_url   = models.URLField(max_length=1024, blank=True, null=True)                     # http://images.craigslist.org/00404_4ELUsqg7uIG_600x450.jpg"
    content         = models.TextField()                                                          # i.e.  2008 Mazda RX-8 40th Anniversary Addition ", "\nEngine \tRotary, 1.3 Liter", ...
    price           = models.IntegerField(default=0, blank=True)                                  # $7500 ->7500
    link            = models.URLField(max_length=1024, blank=True, null=True)                     # CL Link to ad "http://seattle.craigslist.org//see/cto/5655559085.html"
    key             = models.CharField(max_length=256, default=0, blank=True)                     # CL PK 5655559085
    VIN             = models.CharField(max_length=256, default=0, blank=True)                     # ISO standard
    posting_time    = models.DateField()                                                          # posting_time  i.e 2016-06-27 00:30
    last_seen       = models.DateField()                                                          # last_seen     i.e 2016-07-17 10:30
    active          = models.BooleanField(default=True)
    have_counted    = models.BooleanField(default=True)    
    make            = models.ForeignKey('Make', blank=True, null=True)
    models          = models.ForeignKey('Model', blank=True, null=True)

class VehicleImages(models.Model):
    image_url   = models.URLField(max_length=2048, blank=True, null=True)                         # http://images.craigslist.org/00404_4ELUsqg7uIG_600x450.jpg
    image_file  = models.FileField(upload_to='cl/images/%Y/%j_%H_%M_%S',null=True)
    clpost      = models.ForeignKey('ClPost', blank=True, null=True)                  

