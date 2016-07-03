from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from report.models import Make, MakeAlias, Model, Trim, ModelAlias, ClPost, VehicleImages
from collections import OrderedDict

# Create your views here.
def index(request): 
    return render(request,'report/index.html')

def vehicles(request): 
    makes = {}
    make_records = Make.objects.all()
    for make_record in make_records:
        models = {}
        model_records = Model.objects.filter(make=make_record)
        for model_record in model_records:
            try:
                models[model_record.niceName].append(model_record.year)
            except:
                models[model_record.niceName]=[model_record.year]
        ordered_models = OrderedDict(sorted(models.items(), key=lambda t: t[0]))
        makes[make_record.name]=ordered_models
    print makes
    ordered_makes = OrderedDict(sorted(makes.items(), key=lambda t: t[0]))
    return render(request,'report/vehicles.html',{'makes':ordered_makes})

class VehicleList(ListView):
    model = Make
    context_object_name = 'vehicle_makes'

class ModelList(ListView):
    template_name = 'report/model_list.html'

    def get_queryset(self):
        self.make = get_object_or_404(Make, niceName=self.args[0])
        return Model.objects.filter(make=self.make)

def market(request): 
    return render(request,'report/index.html')

def settings(request): 
    return render(request,'report/index.html')

