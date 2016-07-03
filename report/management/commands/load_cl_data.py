###################################################################################
#                     Django Management Command Craigslist Data
#
# Description:
#     Takes Craigslist JSON data and builds the make/model/year tables 
#     The program is invoked as:
#
#     % python manage.py load_cl_data [--overwrite] --path ../../Craigslist.json 
#
# v1.0  DSB     28 Jun 2016     Original program
#
####################################################################################
# cl_format =   {
#     "map_link" : ["https:\/\/maps.google.com\/maps\/preview\/@47.617400,-122.142600,16z"],
#     "address" : [],
#     "paint_color" : ["grey"]
#     "cylinders" : ["4 cylinders"]
#     "map_longitude" : ["-122.142600"]
#     "title" : ["2008 Mazda RX-8 40TH Anniversary Addition"]
#     "link" : "http:\/\/seattle.craigslist.org\/\/see\/cto\/5655559085.html",
#     "VIN" : [],
#     "time" : ["2016-06-27 00:30"]
#     "image_urls" : ["http:\/\/images.craigslist.org\/00404_4ELUsqg7uIG_600x450.jpg"]
#     "fuel" : ["gas"]
#     "v_type" : ["coupe"]
#     "images" : [],
#     "transmission" : ["manual"]
#     "drive" : ["rwd"]
#     "size" : ["compact"]
#     "map_latitude" : ["47.617400"]
#     "condition" : ["excellent"]
#     "map_accuracy" : ["0"]
#     "detail_title" : ["2008 Mazda RX-8 40TH Anniversary Addition"]
#     "odometer" : ["28000"]
#     "price" : ["$7500"]
#     "title_status" : ["rebuilt"]
#     "content" : ["\n        2008 Mazda RX-8 40th Anniversary Addition ", "\nEngine \tRotary, 1.3 Liter",]
#     "key" : ["5655559085"]
#   },

from django.core.management.base import BaseCommand, CommandError
from report.models import Make, Model, MakeAlias, ModelAlias, ClPost, Trim, VehicleImages
from os.path import isfile, splitext
import json
from nested_dict import nested_dict
import sys
import re
import datetime
import uuid
#from time import strptime


def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

class Command(BaseCommand):
    debug_level = 1
    c_makes = []
    c_trim = {}
    c_models = {}
    c_make_aliases = {}
    c_model_aliases = {}

    def __init__(self):
        self.c_makes  = self.makes_list()
        self.c_models =  self.model_dict()        
        self.c_make_aliases   =  self.makes_alias_dict()
        self.c_model_aliases =  self.model_alias_dict()
        self.c_trim = self.trim_dict()


        # if not self.c_make_aliases:
        #     print "Make Aliases Empty"
        # else:
        #     print self.c_make_aliases
        # if not self.c_model_aliases:
        #     print "Model Aliases Empty"
        # else:
        #     print self.c_model_aliases

        # for make in self.c_makes:
        #     print make,
        # print
        # for trim in self.c_trim:
        #     print trim,
        # for model,make in self.c_models.iteritems():
        #     print "%s->%s"%(model,make),
        # for alias,make in self.c_make_aliases.iteritems():
        #     print "%s->%s"%(alias,make)
        # for alias,model in self.c_model_aliases.iteritems():
        #     print "%s->%s"%(alias,model), 
        # for trim,model in self.c_trim_aliases.iteritems():
        #     print "%s->%s"%(trim,model), 

    help = 'Loads the Craigslist Vehicle Database'
    def add_arguments(self, parser):
        parser.add_argument("--infile", nargs="?", dest="infile", help="Path to Craigslist JSON file")
        parser.add_argument("--overwrite", action='store_true', default=False, help="Overwrite existing data in tables?")
        parser.add_argument("--erase", action='store_true', default=False, help="Erase all Craigslist records")       
        parser.add_argument("--debug", action='store_true', default=False, help="Set debug on")

    # Set with debug.set = 1, call with level =1 or gt use -1 to raise CommandError 
    def debug(self,level,message):
        if level <= self.debug_level:
            message=message+"\n"
            sys.stdout.write(message)
        if level < 0:
            raise CommandError(message)

    # Validates json file can be processed 
    def valid_json_file(self, jfile):
        if isfile(jfile) and not jfile.startswith('~'):
            (root,ext) = splitext(jfile)
            if ext.lower() in ('.json',):
                return jfile
            else:
                return ""

    def clean_spider_vals(self,val):
        #print val
        if not val:
            return ""
        if val == "" or val == None:
            return ""
        if isinstance(val, basestring):
            return val
        if isinstance(val,dict):
            return "Error: dict_value"
        try:
            return val[0]
        except TypeError:
            return str(val)

    def str_to_float(self,val):
        if val:
            #print "f->: <%s>"%val
            val = float(val)
        else:
            val = 0
        return val

    def str_to_int(self,val):
        if val:
            #print "i->: <%s>"%val
            val = float(val)
        else:
            val = 0
        return val

    def tuppy_to_dict(self,tups):
        dicky = {}
        for value,refstr in tups:
            #print "Value: %s -> %s"%(value,refstr)
            dicky[refstr.lower()]=value
        return dicky

    def tuppy_lookup(self,lookup,tuppy):
        if lookup:
            lookup_dict = self.tuppy_to_dict(tuppy)
            lookup_keys = lookup_dict.keys()
            if lookup.lower() in lookup_keys:
                return lookup_dict[lookup.lower()]
            else:
                return lookup
        else:
            return ""


    def paint_color(self,color):
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
        return self.tuppy_lookup(color,PAINT_COLOR)


    def drive_type(self,lookup):
        FWD         = 'FD'
        RWD         = 'RD'
        FOURWD      = 'FW'

        DRIVE = (
            (FWD,   'Front Wheel Drive'),
            (RWD,   'Rear Wheel Drive'),
            (FOURWD,'Four Wheel Drive'),
        )
        return self.tuppy_lookup(lookup,DRIVE)

    def transmission_type(self,lookup):
        MANUAL          = 'MA'
        AUTOMATIC       = 'AU'
        OTHER           = 'OT'

        TRANSMISSION = (
            (MANUAL,   'Manual'),
            (AUTOMATIC,'Automatic'),
            (OTHER,    'Other'),
        )
        return self.tuppy_lookup(lookup,TRANSMISSION)

    def condition_type(self,lookup):
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
        return self.tuppy_lookup(lookup,CONDITION)


    def vehicle_type(self,lookup):
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
        return self.tuppy_lookup(lookup,VEHICLE_TYPE)

    def fuel_choices(self,lookup):
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
        return self.tuppy_lookup(lookup,FUEL_CHOICES)

    def vehicle_size(self,lookup):
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
        return self.tuppy_lookup(lookup,VEHICLE_SIZE)

    def title_status(self,lookup):
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
        return self.tuppy_lookup(lookup,TITLE_STATUS)

# time = post['time'], pri_image
    def create_cl_record(self,post):
        #print "map_longitude",post['map_longitude']
        map_longitude   = self.str_to_float(self.clean_spider_vals(post['map_longitude']))
        map_latitude = self.str_to_float(self.clean_spider_vals(post['map_latitude']))
        map_accuracy    = self.str_to_int(self.clean_spider_vals(post['map_accuracy']))
        odometer = self.str_to_int(self.clean_spider_vals(post['odometer']))
        cylobj = re.match( r'^(\d+) cylinders', self.clean_spider_vals(post['cylinders']), re.M|re.I)
        if cylobj:        
            cylinders = self.str_to_int(cylobj.group(1))
        else:
            cylinders = 0
        #print "cylinders: <%s>"%cylinders
        
        priceobj = re.match( r'^\D*(\d+)', self.clean_spider_vals(post['price']), re.M|re.I)
        if priceobj:
            price = self.str_to_int(priceobj.group(1))
        else:
            price = 0

        #print "posting_time: %s"%self.clean_spider_vals(post['posting_time'])
        #Example: ["2016-06-30 14:08"],
        posting_time = datetime.datetime.strptime(self.clean_spider_vals(post['posting_time']), "%Y-%m-%d %H:%M")
        #################
        # lookup codes  #
        #################
        paint_color = self.paint_color(self.clean_spider_vals(post['paint_color']))
        drive = self.drive_type(self.clean_spider_vals(post['drive']))
        transmission = self.transmission_type(self.clean_spider_vals(post['transmission']))
        condition = self.condition_type(self.clean_spider_vals(post['condition']))
        v_type = self.vehicle_type(self.clean_spider_vals(post['v_type']))
        fuel = self.fuel_choices(self.clean_spider_vals(post['fuel']))
        v_size = self.vehicle_size(self.clean_spider_vals(post['v_size']))
        title_status = self.title_status(self.clean_spider_vals(post['title_status']))
        make = post['make']
        model = post['model']
        year = post['year']

        print 'From title: "%s" i am'%self.clean_spider_vals(post['cl_main_title'])
        print "trying to create record for Make: %s Model: %s Year: %s"%(make,model,year)

        make_records = Make.objects.filter(niceName__iexact=make)
        if len(make_records) == 0:
            self.debug(1, "Make record for: %s is missing"%make)
            return(False,False)
        make_record = make_records[0]
        model_records = Model.objects.filter(niceName__iexact=model, year__iexact=year)
        if len(model_records) == 0:
            self.debug(1, "Model record for: %s %s is missing"%(year,model))
            return(False,False)
        model_record = model_records[0]

        clr =  ClPost.objects.create(
                                    address         = self.clean_spider_vals(post['address']),                                                                                          
                                    cl_main_title   = self.clean_spider_vals(post['cl_main_title']),
                                    condition       = condition,
                                    content         = self.clean_spider_vals(post['content']),
                                    cylinders       = cylinders,
                                    detail_title    = self.clean_spider_vals(post['detail_title']),
                                    drive           = drive,
                                    pri_image_url   = self.clean_spider_vals(post['image_urls']),
                                    key             = self.clean_spider_vals(post['key']),
                                    link            = self.clean_spider_vals(post['link']),
                                    map_accuracy    = map_accuracy,
                                    map_latitude    = map_latitude,
                                    map_link        = self.clean_spider_vals(post['map_link']),      
                                    map_longitude   = map_longitude,
                                    odometer        = odometer,
                                    paint_color     = paint_color,
                                    posting_time    = posting_time,
                                    last_seen       = datetime.datetime.now(),
                                    price           = price,
                                    v_size          = v_size,
                                    title_status    = title_status,
                                    transmission    = transmission,
                                    fuel            = fuel,
                                    v_type          = v_type,
                                    VIN             = self.clean_spider_vals(post['VIN']),
                                    make            = make_record,
                                    models          = model_record,
                                    )
        #clr.save()

        #print "Images",
        #print post['images']
        img = None
        for i in post['images']:
            img = VehicleImages.objects.create(image_url = i,image_file = None, clpost = clr)

        return clr,img

    def makes_list(self):
        makes = []
        make_records = Make.objects.all()
        for make_record in make_records:
            makes.append(make_record.niceName)
        return makes

    def makes_alias_dict(self):
        aliases = {}
        alias_records = MakeAlias.objects.all()
        #print "Make alias Records: %s"%alias_records
        for alias_record in alias_records:
            #print "Creating alias: %s"%(alias_record.make.niceName)
            aliases[alias_record.alias]=alias_record.make.niceName 
        return aliases

    def model_alias_dict(self):
        aliases = {}
        alias_records = ModelAlias.objects.all()
        #print "Model alias Records: %s"%alias_records
        for alias_record in alias_records:
            #print "Creating alias: %s"%(alias_record.niceName)
            aliases[alias_record.alias]= alias_record.niceName
        return aliases


    def model_dict(self):
        models = {}
        model_records = Model.objects.all()
        for model_record in model_records:
            models[model_record.niceName]=model_record.make.niceName
        return models

    def trim_dict(self):
        trim = {}
        trim_records = Trim.objects.all()
        for trim_record in trim_records:
            trim[trim_records.trim]=trim_records.model.niceName
        return trim
 
    def parse_year(self):
        pass

    def parse_make(self):
        pass

    def parse_model(self):
        pass

    def delete_records(self):
        e = ClPost.objects.filter()
        for m in e:
            m.delete()

    def debug_global_arrays(self):
        for make in self.c_makes:
            print make,
        print
        print "---------------------------------------------------------------------------------------------------------"
        for model,make in self.c_models.iteritems():
            print "%s->%s"%(model,make),
        print
        print "---------------------------------------------------------------------------------------------------------"
        for alias,make in self.c_make_aliases.iteritems():
            print "%s->%s"%(alias,make), 
        print
        print "---------------------------------------------------------------------------------------------------------"
        for alias,model in self.c_model_aliases.iteritems():
            print "%s->%s"%(alias,model), 
        print
        print "---------------------------------------------------------------------------------------------------------"
     
    # remove all references to word in the list of words
    def remove_words(self,words,word):
        for i in range(words.count(word)):
            words.pop(words.index(word))
        return words

    def find_in_list_and_remove(self,string,thelist):
        found = None
        if not string:
            return(found,string)
        remainder = string
        #print "Working with: %s"%string
        for lfor in thelist:
            pattern = "("+lfor+")"
            #print pattern
            matchobj = re.search(pattern, string, re.I)
            if matchobj:
                found = matchobj.group(1)
                if found:
                    #print "got match: %s"%found
                    remainder = re.sub(pattern, '', string, count=1, flags=re.I)
                    break
        #print "Found: %s, remainder %s"%(found,remainder)
        return(found,remainder)

    def find_and_remove_grp1(self,pattern,string):
        found = ''
        if not string:
            return(found,string)
        remainder = string
        matchobj = re.search(pattern, string, re.I)
        if matchobj:
            found = matchobj.group(1)
            #print "got match object"
            if found:
                #print "found %s"%found                            
                remainder = re.sub(pattern, '', string, count=1, flags=re.I)
            #print "Found: %s, remainder %s"%(found,remainder)
        return(found,remainder)

    def four_digit_year(self,two_digit_year):
        now = datetime.datetime.now()
        if two_digit_year >= 0 and two_digit_year <= int(now.strftime('%y')):
            two_digit_year += 2000
        else:
            two_digit_year += 1900
        return two_digit_year

    # find vehicle model name        
    def parse_title(self,title):
        #make,model,year,trim,rest
        # Cast of characters:
        #     c_makes a list of vehicle manufacturers 
        #     c_make_aliases a dictionary {alias:make}
        #     c_models a dictionary of vehicle names {model:make}
        #     c_model_aliases a dictionary of vehicle alias names {alias:model}
        #     c_trim not used yet

        make_alias = self.c_make_aliases.keys()
        # print make_alias
        models = self.c_models.keys()
        model_aliases = self.c_model_aliases.keys()
        # print model_aliases
        details = {}
        title_orig = title        
        title = title.lower()
        self.debug(2,"Processing Title: %s"%title)
        t_words = title.split()

        # Eliminate any price $nnnn values
        possible_price = []
        pattern = r'\$(\d+,\d\d\d)'
        found,remainder = self.find_and_remove_grp1(pattern,title)
        if found:
            possible_price.append(found)
        else:
            pattern = r'\$(\d+)\.(\d\d)'
            found,remainder = self.find_and_remove_grp1(pattern,title)
            if found:
                possible_price.append(found)
            else:
                pattern = r'\$(\d+)'
                found,remainder = self.find_and_remove_grp1(pattern,title)
                if found:
                    possible_price.append(found)
        title = remainder

        # we don't actually use possible_price since we have it from another field this just 
        # gets it out of the title so it won't be confused.

        # Find and eliminate any four digit years
        # Try to determine year 1990, 2010,'99 '05 etc. but first, only the four
        # digit years ... We have to be careful not to pull out a model name as
        # a year  like S90 or X55 . Also BMW had the 2002 which is very confusing
        # but we are probably safe pulling out them before the models but
        # note we will not be able to get some like the BMW 2002
        # the two digit year has to be approached more carefully but its probably 
        # safe to take any that begin with an apostrophe 

        possible_year = []

        pattern = r'(19\d\d)'
        found,remainder = self.find_and_remove_grp1(pattern,title)
        if found:
            possible_year.append(found)
        else:
            pattern = r'(20\d\d)'
            found,remainder = self.find_and_remove_grp1(pattern,title)
            if found:
                possible_year.append(found)
            else:
                pattern = r'\'(\d\d)'
                found,remainder = self.find_and_remove_grp1(pattern,title)
                if found:
                    year = int(found)
                    possible_year.append(self.four_digit_year(year))
        title = remainder

        
        if possible_year:
            if len(possible_year) == 1:
                details['year'] = possible_year[0]
            else:
                self.debug(1,"Found multiple possible years %s"%possible_year)
                #not sure what to do for now just take the first one
                details['year'] = possible_year[0]

        #find vehicle manufacturers name
        found,remainder = self.find_in_list_and_remove(title,self.c_makes)
        if found:
            details['make'] = found
        else:
            # print "Didn't find manufacture, looking at aliases %s"%make_alias
            found,remainder = self.find_in_list_and_remove(title,make_alias)
            # print "Le Found: %s"%found
            # print "Le Remainder: %s"%remainder
            if found:
                details['make'] = self.c_make_aliases[found]
        title = remainder

        # find model name
        # two possibilities
        #  1) we found the make, so only use known models from the manufacture
        #  2) we didn't find the make so we are on our own
        tmodels = []
        if 'make' in details and details['make']:
            for key,value in self.c_models.iteritems():
                if value == details['make']:
                    tmodels.append(key)
        else:
            tmodels = self.c_models.keys()
        # print "Looking ...."
        found,remainder = self.find_in_list_and_remove(title,tmodels)
        if found:
            details['model'] = found
        else:
            # print "Model Aliases:"
            # print model_aliases
            found,remainder = self.find_in_list_and_remove(title,model_aliases)
            if found:
                details['model'] = self.c_model_aliases[found]
        title = remainder
        # Lets take stock of what we have done so far:
        # 1) we eliminated any prices, they will be in possible_price but we don't care
        # 2) we looked for and eliminated any four digit years, and apostrophe two digit years they will be in details['year'] 
        # 3) we looked for and eliminated any make names, it will be in details['make']
        # 4) we looked for a model name, it will be in details['model'] 

        # Whats left:
        # Any of the afore mentioned could be missing
        #     Make, Model, Year
        # A missing year - we can can still look for two digit years
        # Make without Model - is a failure we probably cant recover from now
        # Model without Make - is actually pretty common and we can reverse from the make to find the model 99% of the time

        # Find two digit years if necessary
        if not possible_year:
            pattern = r'(\d\d)'
            found,remainder = self.find_and_remove_grp1(pattern,title)
            if found:
                year = int(found)
                possible_year.append(self.four_digit_year(year))
            
        # finally smokem if you got em..
        if possible_year:
            if len(possible_year) == 1:
                details['year'] = possible_year[0]
            else:
                self.debug(1,"Found multiple possible years %s"%possible_year)
                #not sure what to do for now just take the first one
                details['year'] = possible_year[0]

        title = remainder

        # OK we have exhausted the year search we still need to do the model no make instance
        # Find make without a model
        possible_make = None

        if 'model' in details and details['model']:
            if 'make' in details and not details['make'] or 'make' not in details:
                try:
                    possible_make = c_models[details['model']]
                except:
                    possible_make = None
            if possible_make:
                details['make'] = possible_make
            details['rest'] = title
        return details


    def parse(self, jfile, overwrite):
        with open(jfile,'r') as f:
            cl_data = json.load(f)
        f.close()
        unknown_keys = []
        make_only=[]
        make_model_only=[]
        make_year_only=[]                 
        model_only=[]
        model_year_only=[]
        year_only=[]

        count = 0
        complete = 0

        for i in cl_data:
            if i['key']:
                count += 1
                key = self.clean_spider_vals(i['key'])
                clr =ClPost.objects.filter(key__iexact=i['key'])
                if clr:
                    self.debug(-1,'Craigslist Post: "%s" key=%s exists' % i['cl_main_title'] ,i['key'])
                    continue
                else:
                    details = {}
                    if 'make' in i:
                        del i['make']
                    if 'model' in i:
                        del i['model']
                    if 'year' in i:
                        del i['year']
                    make = ""
                    model = ""
                    year = ""

                    details = self.parse_title(self.clean_spider_vals(i['cl_main_title']))
                    if 'make' in details and details['make']:
                        make = details['make']
                    if 'model' in details and details['model']:
                        model = details['model']
                    if 'year' in details and details['year']:
                        year = details['year']

                    if make and model and year:
                        complete += 1
                        i['make'] = make
                        i['model'] = model
                        i['year'] = year
                        clr,img = self.create_cl_record(i)

                    elif make and model and not year:
                        t = "Title: %s"%i['cl_main_title']
                        t = t+"->"+"Make: %s"%make 
                        t = t+","+"Model: %s"%model
                        make_model_only.append(t)
                    elif make and not model and not year:
                        t = "Title: %s"%i['cl_main_title']
                        t = t+"->"+"Make: %s"%make 
                        make_only.append(t)
                    elif make and year and not model:
                        t = "Title: %s"%i['cl_main_title']
                        t = t+"->"+"Make: %s"%make 
                        t = t+","+"Year: %s"%year
                        make_year_only.append(t)
                    elif model  and year and not make:
                        t = "Title: %s"%i['cl_main_title']
                        t = t+","+"Model: %s"%model
                        t = t+","+"Year: %s"%year                        
                        model_year_only.append(t)
                    elif model and not year and not make:
                        t = "Title: %s"%i['cl_main_title']
                        t = t+","+"Model: %s"%model
                        model_only.append(t)
                    elif  year and not model  and not make:
                        t = "Title: %s"%i['cl_main_title']
                        t = t+","+"Year: %s"%year                                                
                        year_only.append(t)
            else:
                unknown_keys.append(i)

        cl_logs = {'make_only':make_only,
                'make_model_only':make_model_only,
                'make_year_only':make_year_only,              
                'model_only':model_only,
                'model_year_only':model_year_only,
                'year_only':year_only,
                'unknown_keys':unknown_keys,
                }

        logfile = "./cl_data_log_"+str(uuid.uuid4().get_hex()[0:4])+".json"
        with open(logfile,'w') as f:
            json.dump(cl_logs,f)
        f.close()

        return(count,complete)
                
    # Handle is called when the program is executed its sort of like *void main in a c program
    def handle(self, *args, **options):
        if options['debug']:
            self.debug.set = 1
        if options['erase']:
            if query_yes_no("Are you sure you want to delete all of the Craigslist records this will also delete the averages associated with these records?"):
                sys.stdout.write("Deleting All Craigslist Records")
                #self.delete_records()
            exit(0)
        if options['infile']:
            if self.valid_json_file(options['infile']):
                (count,complete) = self.parse(options['infile'], options['overwrite'])
                percent = float(complete)/count
                sys.stdout.write("Processed %s records of which %s were usable %s\%"%(count,complete,percent))  
            else:
                raise CommandError('"%s" is not a valid json file' % options['infile'])


   
