#!/usr/bin/env python 
# -*- coding: utf-8 -*-
###################################################################################
#                   Django Management Command Load Quad CSV
#
# Description:
#     Takes year make model body_style(trim) quad data and builds the cava tables 
#     The program is invoked as:
#
#     % python manage.py load_quad_csv.py [--write_record] --path ../../data.csv
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
from report.models import Make, Model, Trim
from os.path import isfile, splitext
from nested_dict import nested_dict
from ast import  literal_eval
import unidecode
import sys
import re
import csv

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
        parser.add_argument("--write_record", action='store_true', default=False, help="write data in tables? A safety to allow testing with out actually writing the data")
        parser.add_argument("--erase", action='store_true', default=False, help="Erase all triple records")       
        parser.add_argument("--debug", action='store_true', default=False, help="Set debug on")

    # Set with debug.set = 1, call with level =1 or gt use -1 to raise CommandError 
    def debug(self,level,message):
        if level < self.debug_level:
            self.stdout.write(message)
        if level < 0:
            raise CommandError(message)

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
                                            source = 'VIN',
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
                                                source = 'VIN',
                                                avg_price = 0,
                                                avg_condition = 0,      
                                                avg_location_latitude = 0,
                                                avg_location_longitude = 0,
                                            )
        model_record.save()
        return model_record

    def create_trim_record(self,model_record,trim):
        trim_record = Trim.objects.create(      trim = trim,
                                                niceName = self.niceify(trim),
                                                body_style = trim,
                                                model = model_record,
                                                source = 'VIN',
                                                avg_price = 0,
                                                avg_condition = 0,      
                                                avg_location_latitude = 0,
                                                avg_location_longitude = 0,
                                            )
        trim_record.save()
        return model_record


    def parse(self, infile, write_record):
        count = 0
        new_makes = 0
        new_models = 0
        new_trims = 0

        with open(infile,'r') as f:
            reader = csv.reader(f)
            for row in reader:
                year = row[0].strip()
                make = row[1].strip()
                model = row[2].strip()
                trim = row[3].strip()
                count += 1
                
                if make:
                    make_records = Make.objects.filter(niceName=self.niceify(make))   # First see if the make already exists in the database
                    if not make_records:
                            if write_record:
                                make_record = self.create_make_record(make)                  # else create the record
                            print "created make record: %s"%(make)
                            new_makes += 1
                            if write_record:
                                make_record.save()
                    else:
                        make_record = make_records[0]
                        make_record.source = 'VIN'
                        if write_record:
                            make_record.save()

                    if model:
                        model_records = Model.objects.filter( niceName=self.niceify(model),make=make_record, year = year )
                        if not model_records:
                            if write_record:
                                model_record = self.create_model_record(make_record,model,year)
                            self.debug(2, "created model record: %s %s %s"%(make, year,model))
                            new_models += 1
                            if write_record:
                                model_record.save()
                        else:
                            model_record = model_records[0]
                            model_record.source = 'VIN'
                            if write_record:
                                model_record.save()
                        if trim:
                            trim_records = Trim.objects.filter( niceName=self.niceify(trim),model=model_record )
                            if not trim_records:
                                if write_record:                    
                                    trim_record = self.create_trim_record(model_record,trim)
                                self.debug(2, "created trim record: %s %s %s %s"%(make, year,model,trim))
                                new_trims += 1
                                if write_record:
                                    trim_record.save()
                            else:
                                trim_record = trim_records[0]
                                trim_record.source = 'VIN'
                                if write_record:
                                    trim_record.save()
        f.close()
        
        self.stdout.write("Found %s records"%str(count))
        self.stdout.write("Created %s new make records"%str(new_makes))
        self.stdout.write("Created %s new model records"%str(new_models))
        self.stdout.write("Created %s new trim records"%str(new_trims))
        

    # Handle is called when the program is executed its sort of like *void main in a c program
    def handle(self, *args, **options):
        if options['debug']:
            self.debug.set = 1
        if options['infile']:
            self.parse(options['infile'], options['write_record'])
        else:
            self.debug(-1,"Please provide an --infile")


   
