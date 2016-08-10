#!/usr/bin/env python 
# -*- coding: utf-8 -*-
###################################################################################
#                   Django Management Command Delete Make
#
# Description:
#     Takes make deletes all associated tables 
#     The program is invoked as:
#
#     % python manage.py delete_make.py --erase --make ABC
#
# v1.0  DSB     28 Jun 2016     Original program
#
####################################################################################


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
        parser.add_argument("--make", nargs="?", dest="make", help="Name of make to delete")
        parser.add_argument("--model", nargs="?", dest="model", help="Model name to delete")
        parser.add_argument("--year", nargs="?", dest="year", help="Model year to delete")                
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

    
    def delete(self, make, model, year, erase):
        model_count = 0
        trim_count = 0
        if erase:
            make_records = Make.objects.filter(niceName=self.niceify(make))   # First see if the make already exists in the database
            if make_records:
                make_record = make_records[0]
                model_records = Model.objects.filter( make=make_record, name=make , year=year)
                if  model_records:
                    for model_record in model_records:
                        trim_records = Trim.objects.filter( model=model_record )
                        if trim_records:
                            for trim_record in trim_records:
                                trim_count += 1
                                trim_record.delete()
                        model_record.delete()
                        model_count += 1

        
        self.stdout.write("Deleted %s model records"%str(model_count))
        self.stdout.write("Deleted %s trim records"%str(trim_count))
        

    # Handle is called when the program is executed its sort of like *void main in a c program
    def handle(self, *args, **options):
        if options['debug']:
            self.debug.set = 1
        if options['make'] and options['erase']:
            self.delete(options['make'],options['model'],int(options['year']),options['erase'])
        else:
            self.debug(-1,"Please provide an --make --model --year and --erase")


   
