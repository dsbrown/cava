from django import template
from django.utils.safestring import mark_safe
register = template.Library()
import os
import re

# add {% load abr_tags %}
# call as: {% example arg1 arg2 %} 

@register.filter
def fileBaseName(string):
	return re.sub(r'(.+)\?.+','\\1',os.path.basename(string))

@register.simple_tag
def example(arg1,arg2):
    data = ''
    data += "%s,%s"%(arg1,arg2)
    return mark_safe(data)


# this is some stuff I am working on to build a table out cetain fields in a form
# its not even close to working yet
@register.filter
def starts_with(field,starts_with):
    if field.startswith(starts_with):
        return True
    else:
        return False
        #  if key.startswith(starts_with):
        #     fields_with[key]=value
        # else:
        #     fields_without[key]=value

@register.filter
def tbl_state(val):
    return val



@register.simple_tag
def print_site_tbl(form,number_cols,starts_with):
    data = ''
    # ne = len(form.fields)
    # nr = ne/number_cols
    # colw = 10/number_cols
    # keys = form.fields.keys()
    # for i in xrange(nr):
    #     data += '<div class="row"> <div class="col-md-1"> </div>'
    #     for j in xrange(number_cols):
    #         k = keys.pop()
    #         field = form.fields[k]
    #         data += '<div class="col-md-%s">[%s]'%(colw,k)
    #         data += field
    #         data += '</div>'
    #     data += '<div class="col-md-1"> </div>'
    #     data += '</div>'
    # # for key, value in form.fields.iteritems():
    # #     if key.startswith(starts_with):
    # #         data += "%s"%(key)
    # data += str(nr)
    return mark_safe(data)
