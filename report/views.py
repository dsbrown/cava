from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from report.models import Make, MakeAlias, Model, Trim, ModelAlias, ClPost, VehicleImages
from collections import OrderedDict
from django.core.urlresolvers import reverse_lazy


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

class MakeCreate(CreateView):
    model = Make
    fields = ['name','niceName','edmunds_id']

class MakeUpdate(UpdateView):
    model = Make
    fields = ['name','niceName','edmunds_id']

    def get_object(self):
        self.make_record = get_object_or_404(Make, name=self.kwargs['make'])
        return get_object_or_404(Make, pk=self.make_record.pk)

class MakeDelete(DeleteView):
    model = Make

    def get_object(self):
        self.make_record = get_object_or_404(Make, name=self.kwargs['make'])
        return get_object_or_404(Make, pk=self.make_record.pk)

    success_url = reverse_lazy('vehicles')

class ModelCreate(CreateView):
    model = Model
    template_name = 'report/model_add.html'
    fields = ['name','niceName','edmunds_year_id', 'make', 'year', 'edmunds_year_id' ]

    success_url = reverse_lazy('vehicles')

class ModelCreateMake(CreateView):
    model = Model
    template_name = 'report/model_add.html'
    fields = ['name','niceName','edmunds_year_id', 'make', 'year', 'edmunds_year_id' ]

    def get_initial(self):
        print self.kwargs['make']
        self.make_record = get_object_or_404(Make, name__iexact=self.kwargs['make'])
        # Get the initial dictionary from the superclass method
        initial = super(ModelCreateMake, self).get_initial()
        # Copy the dictionary so we don't accidentally change a mutable dict
        initial = initial.copy()
        initial['make'] = self.make_record
        return initial

class ModelUpdate(UpdateView):
    model = Model
    fields = ['name','niceName','edmunds_year_id', 'make', 'year', 'edmunds_year_id' ]

    def get_object(self):
        self.make_record  = get_object_or_404(Make,  name__iexact=self.kwargs['make'])
        #self.test_model_record = Model.objects.filter(year__iexact=self.kwargs['year'], make=self.make_record)
        self.model_record = get_object_or_404(Model, niceName__iexact=self.kwargs['model'], year=self.kwargs['year'], make=self.make_record)
        return get_object_or_404(Model, pk=self.model_record.pk)

class ModelDelete(DeleteView):
    model = Model
    fields = ['name','niceName','edmunds_year_id', 'make', 'year', 'edmunds_year_id' ]

    def get_object(self):
        return get_object_or_404(Model, pk=self.kwargs['pk'])

    success_url = reverse_lazy('vehicles')


