from django.shortcuts import render
from try_app1.models import Marks
from django.db.models import Avg

def docalc():
    return Marks.objects.all().aggregate(Avg('english'))['english__avg']

def main(request):
    #eng_avg = Marks.objects.all().aggregate(Avg('english'))['english__avg']
    eng_avg = docalc()
    mydict = {eng_avg : eng_avg}
    return render(request,'home.html',{'mydict':mydict})