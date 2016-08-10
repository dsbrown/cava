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
import csv
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


    help = 'Loads the Make/Model/Year CSV Vehicle Database'
    def add_arguments(self, parser):
        parser.add_argument("--infile", nargs="?", dest="infile", help="Path to CSV file")
        parser.add_argument("--overwrite", action='store_true', default=False, help="Overwrite existing data in tables?")
        parser.add_argument("--erase", action='store_true', default=False, help="Erase all matching records")       
        parser.add_argument("--debug", action='store_true', default=False, help="Set debug on")

    # Set with debug.set = 1, call with level =1 or gt use -1 to raise CommandError 
    def debug(self,level,message):
        if level <= self.debug_level:
            message=message+"\n"
            sys.stdout.write(message)
        if level < 0:
            raise CommandError(message)

    # Validates json file can be processed 
    def valid_csv_file(self, cfile):
        if isfile(cfile) and not cfile.startswith('~'):
            (root,ext) = splitext(cfile)
            if ext.lower() in ('.csv',):
                return cfile
            else:
                return ""

    
    def tuppy_to_dict(self,tups):
        dicky = {}
        for value,refstr in tups:
            #print "Value: %s -> %s"%(value,refstr)
            dicky[refstr.lower()]=value
        return dicky



    def delete_records(self):
        e = Make.objects.all()
        for m in e:
            pass
            #m.delete()

    # from USA Mileage Data
    #  http://www.fueleconomy.gov/feg/ws/index.shtml
    #comb08  cylinders   displ   drive   fuelType    fuelType1   make    model   trany   VClass  year    modifiedOn
    def parse(self, cfile, overwrite):

        with open(cfile, 'rb') as csvfile:
            linereader = csv.reader(csvfile, delimiter=',')
            for row in linereader:
                print row
         
    # Handle is called when the program is executed its sort of like *void main in a c program
    def handle(self, *args, **options):
        if options['debug']:
            self.debug.set = 1
        if options['erase']:
            if query_yes_no("Are you sure you want to delete all of the Make/Model records this will also delete the averages associated with these records?"):
                self.stdout.write("Deleting All Make/Model Records")
                self.delete_records()
            exit(0)
        if options['infile']:
            if self.valid_csv_file(options['infile']):
                self.parse(options['infile'], options['overwrite'])
            else:
                self.debug(-1,'"%s" is not a valid csv file' % options['infile'])

   
