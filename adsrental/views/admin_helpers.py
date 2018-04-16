from __future__ import unicode_literals

from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.admin.lead_admin import LeadAdmin


class AdminActionView(View):
    @method_decorator(login_required)
    def get(self, request, model_name, action_name, object_id):
        next_url = request.GET.get('next')
        admin_models = {
            'LeadAdmin': LeadAdmin,
        }
        admin_model_cls = admin_models[model_name]
        queryset = admin_model_cls.model.objects.filter(pk=object_id)

        result = getattr(admin_model_cls, action_name)(admin_model_cls, request, queryset)
        if result:
            return result

        return HttpResponseRedirect(next_url)

    @method_decorator(login_required)
    def post(self, request, model_name, action_name, object_id):
        admin_models = {
            'LeadAdmin': LeadAdmin,
        }
        next_url = request.GET.get('next')
        admin_model_cls = admin_models[model_name]
        queryset = admin_model_cls.model.objects.filter(pk=object_id)

        result = getattr(admin_model_cls, action_name)(admin_model_cls, request, queryset)
        if result:
            return result

        return HttpResponseRedirect(next_url)
