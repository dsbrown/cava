###################################################################################
#                     Django Management Command Edmungs Data
#
# Description:
#     Takes Edmunds JSON data and builds the make/model/year tables 
#     The program is invoked as:
#
#     % python manage.py load_edmunds_data [--overwrite] --path ../../Edmunds.json 
#
# v1.0  DSB     28 Jun 2016     Original program
#
####################################################################################
# edmunds_format =    {
#                       "makes" : [
#                         {
#                           "id" : 200347864,
#                           "models" : [
#                             {
#                               "id" : "AM_General_Hummer",
#                               "years" : [
#                                 {
#                                   "id" : 3407,
#                                   "year" : 1998
#                                 },
#                                 {
#                                   "id" : 1140,
#                                   "year" : 1999
#                                 },
#                                 {
#                                   "id" : 305,
#                                   "year" : 2000
#                                 }
#                               ],
#                               "name" : "Hummer",
#                               "niceName" : "hummer"
#                             }
#                           ],
#                           "name" : "AM General",
#                           "niceName" : "am-general"
#                         },
#                     ],
#                       "makesCount" : 62
#                     }


from django.core.management.base import BaseCommand, CommandError
from report.models import Make, Model
from os.path import isfile, splitext
import json
from nested_dict import nested_dict
import sys

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


    help = 'Loads the Edmunds Vehicle Database'
    def add_arguments(self, parser):
        parser.add_argument("--infile", nargs="?", dest="infile", help="Path to Edmunds JSON file")
        parser.add_argument("--overwrite", action='store_true', default=False, help="Overwrite existing data in tables?")
        parser.add_argument("--erase", action='store_true', default=False, help="Erase all Edmunds records")       
        parser.add_argument("--debug", action='store_true', default=False, help="Set debug on")

    # Set with debug.set = 1, call with level =1 or gt use -1 to raise CommandError 
    def debug(self,level,message):
        if level >= self.debug_level:
            self.stdout.write(message)
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

    def create_make_record(self,make):
        make_record = Make.objects.create(  niceName = make["niceName"],
                                            edmunds_id = make["id"], 
                                            name = make["name"],
                                          )
        make_record.save()
        return make_record

    def create_model_record(self,make_record,model,model_year):
        model_record = Model.objects.create(    name = model["name"],
                                                niceName = model["niceName"],
                                                edmunds_id = model["id"], 
                                                edmunds_year_id = model_year['id'],
                                                year=model_year['year'],
                                                make = make_record,
                                                trim = "",
                                                alias = None,
                                                avg_price = 0,
                                                avg_condition = 0,      
                                                avg_location_latitude = 0,
                                                avg_location_longitude = 0,
                                            )
        model_record.save()
        return model_record

    def validate_make_record(self,make_record,make,overwrite):               # These things must be done delicately or you ruin the spell
        if overwrite:
            make_record.niceName = make["niceName"]
            make_record.edmunds_id = make["id"]
            make_record.alias = None
            make_record.name = make["name"]
            make_record.save()
        elif not make_record.edmunds_id or make_record.edmunds_id != make["id"]:
            make_record.edmunds_id = make["id"]
            make_record.name = make["name"]
            make_record.save()
        return True

    def validate_model_record(self,model_record,make_record,model,model_year,overwrite):
        if overwrite:
            model_record.delete()
            model_year = self.create_model_record(make_record,model,model_year)
        else:
            if not model_record.edmunds_id or model_record.edmunds_id != model["id"]:
                model_record.edmunds_id = model["id"]
            if not model_record.edmunds_year_id or model_record.edmunds_year_id != model_year['id']:
                model_record.edmunds_year_id = model_year['id']
            if model_record.year != model_year['year']:
                model_record.year = model_year['year']
            model_record.name = model["name"]
            model_record.save()
        return True

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

    def parse(self, jfile, overwrite):
        with open(jfile,'r') as f:
            edmunds_data = json.load(f)
        f.close()
        for key in edmunds_data.keys():
            self.debug(2,key)
        self.debug(1, "Using Edmunds Data at %s"%jfile)
        make_count = 0
        for make in edmunds_data["makes"]:
            self.debug(1, "%s"%make['name'])
            make_count += 1
            make_records = Make.objects.filter(niceName=make['niceName'])   # First see if the make already exists in the database
            if make_records:
                make_record = make_records[0]                               # If it does, then see if it has the Edmunds ID's, if not overwrite with Edmunds data
                self.validate_make_record(make_record,make,overwrite)       # if overwrite, do not delete the record because model records point to it
            else:                                                            
                make_record = self.create_make_record(make)                 # else create the record

            for model in make['models']:
                for model_year in model['years']:
                        model_records = Model.objects.filter(niceName=model['niceName'],
                                                             year  =model_year['year'])
                        if model_records:
                            model_record = model_records[0]
                            self.validate_model_record(model_record,make_record,model,model_year,overwrite)
                        else:
                            model_records = self.create_model_record(make_record,model,model_year)

        if make_count == edmunds_data["makesCount"]:
            self.debug(1, "Found %s vehicle makes which is what I expected to find"%str(make_count))
        else:
            self.debug(1, "Found %s vehicle makes but expected %s"%str(make_count),str(edmunds_data["makesCount"]))

    # Handle is called when the program is executed its sort of like *void main in a c program
    def handle(self, *args, **options):
        if options['debug']:
            self.debug.set = 1
        if options['erase']:
            if query_yes_no("Are you sure you want to delete all of the Edumnds records this will also delete the averages associated with these records?"):
                self.stdout.write("Deleting All Edumnds Records")
                self.delete_records()
            exit(0)
        if options['infile']:
            if self.valid_json_file(options['infile']):
                self.parse(options['infile'], options['overwrite'])
            else:
                self.debug(-1,'"%s" is not a valid json file' % options['infile'])


   
