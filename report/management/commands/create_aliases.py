###################################################################################
#                 Django Management Command Create Aliases Data
#
# Description:
#     Associates proper vehicle manufactures names with their aliases like
#     Chevrolet - Chevy
#
#     % python manage.py create_aliases 
#
# v1.0  DSB     28 Jun 2016     Original program
#
####################################################################################
from django.core.management.base import BaseCommand, CommandError
from report.models import Make, MakeAlias, ModelAlias
from os.path import isfile, splitext
import sys

MAKE_ALIASES = {
                'chevy':'chevrolet',
                'vw':"volkswagen",
                'vdub':'volkswagen',
               }

MODEL_ALIASES = {
                'bug':'beetle',
                'beatle':'beetle',
                'dually':'pickup',
                'pickup':'pickup',
               }

TRIM_ALIASES = {}

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

    help = 'Loads aliases for vehicle makes'
    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action='store_true', default=False, help="Overwrite existing data in tables?")
        parser.add_argument("--erase", action='store_true', default=False, help="Erase all Craigslist records")       
        parser.add_argument("--debug", action='store_true', default=False, help="Set debug on")

    # Set with debug.set = 1, call with level =1 or gt use -1 to raise CommandError 
    def debug(self,level,message):
        if level >= self.debug_level:
            self.stdout.write(message)
        if level < 0:
            raise CommandError(message)

    def create_make_aliases(self,alias,make_record):
        alias_record = MakeAlias.objects.create(  
                                            alias = alias,
                                            make = make_record,
                                            )
        alias_record.save()
        self.stdout.write("Alias  %s created which refers to %s"%(alias_record.alias, make_record.niceName))

    def make_aliases(self,options):
        for alias,name in MAKE_ALIASES.iteritems():
            make_records  = Make.objects.filter(niceName__iexact=name)
            alias_records = MakeAlias.objects.filter(alias=alias)
            if make_records:
                make_record  = make_records[0]
            else:
                self.stdout.write("Make Record %s is not in the database, aborting"%name)
                self.stdout.write("Make Object: %s"%make_records)
                exit(1)

            if alias_records:
                alias_record = alias_records[0]
                self.debug(1,"Alias record %s exists for alias %s which refers to %s"%(alias_record.pk, alias_record.alias, make_record.niceName) )
                if options['overwrite']:
                    alias_record.delete()
                    self.create_make_aliases(alias,make_record)
            else:
                self.create_make_aliases(alias,make_record)

    def create_model_aliases(self,alias,name):
        # try:
        #     trim = TRIM_ALIASES[name]
        # except:
        #     trim = ""
        alias_record = ModelAlias.objects.create(  
                                                alias = alias,
                                                niceName = name,
                                                )
        alias_record.save()
        self.stdout.write("Alias  %s created which refers to %s."%(alias_record.alias, alias_record.niceName))

    def model_aliases(self,options):
        for alias,name in MODEL_ALIASES.iteritems():
            alias_records = MakeAlias.objects.filter(alias=alias)
            if alias_records:
                alias_record = alias_records[0]
                self.debug(1,"Alias record %s exists for alias %s which refers to %s"%(alias_record.pk, alias_record.alias, make_record.niceName) )
                if options['overwrite']:
                    alias_record.delete()
                    self.create_model_aliases(alias,name)
            else:
                self.create_model_aliases(alias,name)

    # Handle is called when the program is executed its sort of like *void main in a c program
    def handle(self, *args, **options):
        if options['debug']:
            self.debug.set = 1
        if options['erase']:
            if query_yes_no("Are you sure you want to delete all of the alias records?"):
                self.stdout.write("Deleting All Alias Records")
                for r in MakeAlias.objects.all():
                    r.delete()
                for r in ModelAlias.objects.all():
                    r.delete()       
            exit(0)
        self.make_aliases(options)
        self.model_aliases(options)
        


   
