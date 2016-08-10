#!/usr/bin/env python 
# -*- coding: utf-8 -*-
###################################################################################
#                    Django Management Command Load Triple Data
#
# Description:
#     Takes make model year triple data and builds the make/model/year tables 
#     The program is invoked as:
#
#     % python manage.py load_triple_data [--overwrite] --path ../../data.sql
#
# v1.0  DSB     28 Jun 2016     Original program
#
####################################################################################
# triple_format:
# INSERT INTO VehicleModelYear (year, make, model) VALUES (1909, 'Ford', 'Model T'),
# (1926, 'Chrysler', 'Imperial'),
# (1948, 'Citroën', '2CV'),
# (1950, 'Hillman', 'Minx Magnificent'),
# ... etc.

from django.core.management.base import BaseCommand, CommandError
from report.models import Make, Model
from os.path import isfile, splitext
from nested_dict import nested_dict
from ast import  literal_eval
import unidecode
import sys
import re

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

    help = 'Loads the triple database into CAVA'
    def add_arguments(self, parser):
        parser.add_argument("--infile", nargs="?", dest="infile", help="Path to triple file")
        parser.add_argument("--overwrite", action='store_true', default=False, help="Overwrite existing data in tables?")
        parser.add_argument("--erase", action='store_true', default=False, help="Erase all triple records")       
        parser.add_argument("--debug", action='store_true', default=False, help="Set debug on")

    # Set with debug.set = 1, call with level =1 or gt use -1 to raise CommandError 
    def debug(self,level,message):
        if level >= self.debug_level:
            self.stdout.write(message)
        if level < 0:
            raise CommandError(message)


    def strip_accents(self,s):
        #return unicodedata.normalize('NFD', s)

        #n = unicode(s,'utf-8')
        s = unidecode.unidecode(s)
        return s
        #return .join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        #return s

    def niceify(self,s):
        if not isinstance(s, basestring):
            s = str(s)
        s = s.lower()
        s = s.strip()
        s = "-".join(s.split())
        return s



    def create_make_record(self,make):
        make_record = Make.objects.create(  niceName = self.niceify(make),
                                            edmunds_id = 0, 
                                            name = make,
                                            source = 'GHB',
                                          )
        make_record.save()
        return make_record

    def create_model_record(self,make_record,model,year):
        model_record = Model.objects.create(    name = model,
                                                niceName = self.niceify(model),
                                                edmunds_id = 0, 
                                                edmunds_year_id = 0,
                                                year=year,
                                                make = make_record,
                                                source = 'GHB',
                                                avg_price = 0,
                                                avg_condition = 0,      
                                                avg_location_latitude = 0,
                                                avg_location_longitude = 0,
                                            )
        model_record.save()
        return model_record

    def delete_records(self):
        e = Model.objects.filter(edmunds_id__gt=0)
        for m in e:
            m.delete()

        e = Model.objects.filter(edmunds_year_id__gt=0)
        for m in e:
            m.delete()

        e = Make.objects.filter(edmunds_id__gt=0)
        for m in e:
            m.delete()

    def parse(self, infile, overwrite):
        count = 0
        new_makes = 0
        new_models = 0
        with open(infile,'r') as f:
            next(f)
            for line in f:
                year = None
                make = None
                model = None
                #print line
                matchobj = re.search(r"(\d+), '(.+?)', '(.+)'", line, re.I)
                if matchobj:
                    #print "matchobj"
                    year  = matchobj.group(1)
                    make  = matchobj.group(2)
                    model = matchobj.group(3)
                    #model = model.encode('utf-8')
                    # model = unicode(model)
                    # model = unicode.decode(model)
                    #model = self.strip_accents(model)
                    # model = unidecode.unidecode(model)
                    # model = str(model)
                    # model = model.decode("ascii","ignore")            # fixes Citroën -> Citroen
                    #print "Year:%s, Make:%s, Model:%s"%(year,make,model)
                    count += 1
                else:
                    print "Regex failed on: %s"%line
                    next

                make_records = Make.objects.filter(niceName=self.niceify(make))   # First see if the make already exists in the database
                if not make_records:
                    make_record = self.create_make_record(make)                  # else create the record
                    print "created make record: %s"%(make)
                else:
                    make_record = make_records[0]
                    make_record.source = 'GHB'
                    make_record.save()

                #model_records = Model.objects.filter( niceName=self.niceify(model),year = year,make = make_record )
                model_records = Model.objects.filter( niceName=self.niceify(model),year = year )
                if not model_records:
                    model_records = self.create_model_record(make_record,model,year)
                    print "created model record: %s %s %s"%(make, year,model)
                    new_models += 1
                else:
                    model_record = model_records[0]
                    model_record.source = 'GHB'
                    model_record.save()
        f.close()

        
        self.debug(1, "Found %s records"%str(count))
        self.debug(1, "Created %s new make records"%str(new_makes))
        self.debug(1, "Created %s new model records"%str(new_models))
        

    # Handle is called when the program is executed its sort of like *void main in a c program
    def handle(self, *args, **options):
        if options['debug']:
            self.debug.set = 1
        if options['erase']:
            if query_yes_no("Are you sure you want to delete all of the make/model records this will also delete the averages associated with these records?"):
                self.stdout.write("Deleting All Records")
                self.delete_records()
            exit(0)
        if options['infile']:
                self.parse(options['infile'], options['overwrite'])
        else:
            self.debug(-1,"Please provide an --infile")


   
