###################################################################################
#                   Django Management Command load EPA Data
#
# Description:
#     Takes EPA data saved as XLS and builds the make/model/year records 
#     The program is invoked as:
#
#     % python manage.py load_epa_data [--overwrite] --path epadata.xlsx 
#
# v1.0  DSB     5 Jul 2016     Original program
#
####################################################################################

from django.core.management.base import BaseCommand, CommandError
from report.models import Make, Model, MakeAlias, ModelAlias, ClPost, Trim, VehicleImages
from os.path import isfile, splitext
from openpyxl import load_workbook
from nested_dict import nested_dict
import sys
import re
import datetime
import uuid


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

def query_multiselct(question, answers):
    """Ask a multiple choice question via raw_input() and return the answer.

    "question" is a string that is presented to the user.
    question = "What is your favorite color"
    "answers" is an array of the questions
    answers = [blue,red,orange,green]
    
    The "answer" return value is the index into the answer array response i.e 2 for orange
    """

    while True:
        sys.stdout.write(question + "?")
        c = 1
        number = 0
        for answer in answers:
            sys.stdout.write(c + " " + question + "?")
            c += 1
        choice = raw_input().lower()
        try:
            number = long(choice)
        except:
            pass
        if number >0 and number <= len(answers)+1:
            return number-1
        else:
            sys.stdout.write("Must be a number between 1 and %s"%len(answers)+1)


class Command(BaseCommand):
    debug_level = 1
    s_make_model_years = {}
    s_makes = {}
    s_new_makes = []
    s_new_models = []

    help = 'Loads the Make/Model/Year CSV Vehicle Database'
    def add_arguments(self, parser):
        parser.add_argument("--infile", nargs="?", dest="infile", help="Path to CSV file")
        parser.add_argument("--overwrite", action='store_true', default=False, help="Overwrite existing data in tables?")
        parser.add_argument("--statistics", action='store_true', default=False, help="Print interesting information about data")        
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
    def valid_xlsx_file(self, cfile):
        if isfile(cfile) and not cfile.startswith('~'):
            (root,ext) = splitext(cfile)
            if ext.lower() in ('.xlsx',):
                return cfile
            else:
                return ""

    def delete_records(self):
        e = Make.objects.all()
        for m in e:
            pass
            #m.delete()

    MUNGED_NAMES =  { 'chevrolet':'',
                     'bi-fuel':'',}

    def munge_model_names(self,model):
        if isinstance(model,basestring):
            # deal with compound models like: silver-spur/silver-dawn assumes only two per compound which is mostly true
            models =[model]
            matchobj = re.search(r'(.*?)(\/)(.*)', model, re.I)
            if matchobj and matchobj.group(2) :
                models = [matchobj.group(1),matchobj.group(3)]
                # print model
                #print "got compound: %s"%models
            new_models = []
            for model in models:
                # map left to right
                for find,replace in self.MUNGED_NAMES.iteritems():
                    model = model.replace(find,replace)

                # remove parenthetical in models such as    -(puerto-rico-only),  -(bi-fuel),   -(cargo-van),   -(dedicated-cng) -(5-doors)
                # matchobj = re.search(r'(.*?)-*(\(.+?\))(.*)', model, re.I)
                # if matchobj and matchobj.group(2):
                #     # print "got match: %s"%found
                #     model = matchobj.group(1)+matchobj.group(3)
                    # print "Model: %s"%model

                # replace multiple runs of -- with -
                model = re.sub(r'-{2,}','-',model)

                # remove trailing -
                if model.endswith('-'):
                    model = model[:len(model)-1]

                matchobj = re.search(r'(\w+)-+$', model, re.I)
                model = re.sub(r'-+$','',model)
                new_models.append(model)

            return new_models
        else:
            #print "Found long:",
            #print model
            models = [str(model)]
            return models

    def get_model(self,model):
        rejected = False
        possible_models = []

        # try to find the model 
        model_records = Model.objects.filter(niceName__iexact=model, year = year, make=make_record)
        if model_records:
                model_found = model
        else:
            # We didn't expect to find it on the first try so ...
            # look at every word and see if we can pull a model out
            # first try a tight filter
            for i in model.split("-"):
                model_records = Model.objects.filter(niceName__iexact=i, year = year, make=make_record)
                if model_records:
                    #Take the first one because its most likely the model name i.e. 911 Turbo GT is 911 or Outback Turbo AWD the first is usually the model
                    model_found = i
            if not model_found:
                # Maybe we don't have information on a new year for the model
                for i in model.split("-"):
                    model_records = Model.objects.filter(niceName__iexact=i, make=make_record)
                    if model_records:
                        #Take the first one because its most likely the model name i.e. 911 Turbo GT is 911 or Outback Turbo AWD the first is usually the model
                        if query_yes_no("Do you want to create %s %s for the new year %s?"%(make,model,year)):
                            self.stdout.write("Creating Model")
                            print model_found = create_model_here

                            model_found = Model.objects.create( niceName = model,
                                                                make = make_record,
                                                                name = deniceify(model),
                                                                year=model_year['year'],
                                                                )
                        else:
                            rejected = True
            # Then this is absolutely a new model lets ask
            if not model_found and not rejected:
                pm=model.split("-")
                possible_models = (pm[1],pm[1:],"Don't create model")
                answer = query_multiselct("Do you want me to create a model for the %s:"%year, possible_models)
                if answer < 2:
                    model = possible_models[answer]
                    model_found = Model.objects.create( niceName = model,
                                                        make = make_record,
                                                        name = deniceify(model),
                                                        year=model_year['year'],
                                                        )
                else:
                    #add record to rejected heap
                    rejected = True

        return model_record
       


    
    # { u'cylinders': 6L, u'displ': 4.3, u'modifiedon': u'tue-jan-01-00:00:00-est-2013', u'make': u'chevrolet', 
    #   u'drive': u'4-wheel-or-all-wheel-drive', u'vclass': u'standard-pickup-trucks', u'trany': u'automatic-4-spd', 
    #  u'fueltype1': u'regular-gasoline', u'year': 1995L, u'comb08': 14L, u'model': u'pickup-2500-4wd', u'fueltype': u'regular'}
    def process_record(self,datadict):
        #print datadict
        make = datadict['make']
        epa_record = datadict['modifiedon']
        year = str(datadict['year'])
        model = datadict['model']

        # Determine make of vehicle and get record
        make_records = Make.objects.filter(niceName__iexact=make)
        if not make_records:
            self.s_new_makes.append(make)
            self.s_new_models.append(model)
        else:
            make_record = make_records[0] 

        try:
            self.s_makes[make] += 1
        except:
            self.s_makes[make] = 1

        #print "Munged: %s"%model,
        models = self.munge_model_names(model)
        #print " -> %s"%models

        # These records have a lot of trim details so we are going to try to pull the model out of the 
        # description and use that as a trim detail
        for model in models:
            model_record = get_model(model)
            

            try:
                s_make_model_years[make][model].append(year)
            except:
                m = {}
                m['model'] = []
                m['model'].append(str(year))
                self.s_make_model_years[make]=m
        
                if not model_found:
                    self.s_new_models.append(model)

            ##########################################
            #   Now we finally add the trim records
            ##########################################

        

    def niceify(self,s):
        if isinstance(s, basestring):
            s = s.lower()
            s = s.strip()
            s = "-".join(s.split())
        return s

    def deniceify(self,s):
        if isinstance(s, basestring):
            s = " ".join(s.split("-"))
            s = s.title()
            s = s.strip()
        return s


    # from USA Mileage Data
    #  http://www.fueleconomy.gov/feg/ws/index.shtml
    #comb08  cylinders   displ   drive   fuelType    fuelType1   make    model   trany   VClass  year    modifiedOn
    def parse(self, cfile, options):
        self.stdout.write('Parsing EPA Data at %s'%cfile)
        wb = load_workbook(filename=cfile, data_only=True)
        ws = wb.worksheets[0]
        headers=[]
        first_row = True
        for row in ws.rows:
            c = 0
            t = {}
            for cell in row:
                if first_row:
                    headers.append(self.niceify(cell.value))
                else:
                     t[headers[c]] = self.niceify(cell.value)
                     c += 1                
            if first_row:
                first_row = False
                self.stdout.write('Column Header [%s]'%headers)
            else:
               self.process_record(t)

    
    def unique_keys(self,datadict):
        d  = {}
        for e in datadict:
            d[e]=1
        return d.keys()
         
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
            if self.valid_xlsx_file(options['infile']):
                self.parse(options['infile'], options)
                if options['statistics']:
                    self.s_new_makes = self.unique_keys(self.s_new_makes)

                    print "%s New Makes"%len(self.s_new_makes)
                    for i in self.s_new_makes:
                        print i,
                    print

                    self.s_new_models = self.unique_keys(self.s_new_models)

                    print "%s New Models"%len(self.s_new_models)
                    for i in self.s_new_models:
                        print i,
                    print
            else:
                self.debug(-1,'"%s" is not a valid xlsx file' % options['infile'])

   
