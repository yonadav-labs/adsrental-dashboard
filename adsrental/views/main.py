from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class MainView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'main.html', dict(
            user=request.user,
        ))
