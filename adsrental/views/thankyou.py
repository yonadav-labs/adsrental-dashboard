from django.views import View
from django.shortcuts import render


class ThankyouView(View):
    def get(self, request):
        return render(request, 'thankyou.html')
