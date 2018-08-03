import csv
import json

from dateutil import parser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from project.forms import PostForm
from .models import Transaction, Data
from project.forms import UpdateForm
from project.GmailParser import Parser
from project.models import Payment, KaspiParser, NurbankParser, KazkomParser, ToursimParser
import logging
import datetime
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd


logger = logging.getLogger(__name__)


# Create your views here.

class FormView(TemplateView):
    template_name = 'project/transaction_list.html'

    global seq, snon, columns

    def get(self, request):
        form = PostForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        global seq, snon, columns
        columns = ['id', 'date', 'transfer', 'fee', 'total', 'bank']
        form = PostForm(request.POST)
        but = request.POST.get('submit')

        if form.is_valid():
            name = form.cleaned_data['name']
            start = form.cleaned_data['start_date']
            end = form.cleaned_data['end_date']
            transactions = Transaction.objects.filter(name__contains=name, date__range=[start, end])

            filename = 'C:/Users/acer e15/Desktop/aviata/docs/api.json'
            myfile = open(filename, 'r', encoding='Latin-1')
            json_data = json.load(myfile)
            equal = []
            notequal = []
            for data in json_data:
                if data['payment_code'] == name.upper():
                    tr = Transaction.objects.filter(id=data['order_id'])

                    if len(tr) > 0:
                        for i in tr:
                            if i.transfer == data['payment_amount']:
                                a = Data(i.id, i.date, i.transfer, i.fee, i.total, i.name)
                                b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                         data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata')
                                equal.append(a)
                                equal.append(b)

                            else:
                                a = Data(i.id, i.date, i.transfer, i.fee, i.total, i.name)
                                b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                         data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata')
                                notequal.append(a)
                                notequal.append(b)
            seq = equal
            snon = notequal

            args = {'form': form, 'equal': equal, 'notEqual': notequal}

            # tr = Transaction.objects.filter(id=4)
            # return redirect('/transaction')
            # check isequal or not
            # args = {'form': form, 'transactions': transactions}
            return render(request, self.template_name, args)

        if (but == "download"):
            global seq
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment;filename=export_equal.csv'
            writer = csv.writer(response)
            writer.writerow(columns)
            for obj in seq:
                writer.writerow([getattr(obj, field) for field in columns])
            return response

        if (but == "nondownload"):
            global snon
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment;filename=export_not_equal.csv'
            writer = csv.writer(response)
            writer.writerow(columns)
            for obj in snon:
                writer.writerow([getattr(obj, field) for field in columns])
            return response




ids = [1, 2, 3, 4]
names = ['kaspi', 'nurbank', 'tourism', 'kazkom']


class ParseForm(TemplateView):
    template_name = 'project/update_list.html'
    global s
    simplelist = []
    for i in range(0, len(names)):
        files = []
        th = Parser(names[i], files)
        th.start()
        file = th.file
        x = Payment(names[i], file)
        simplelist.append(x)

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        # getFilenames---------------
        # simplelist = []
        submitbutton = request.POST.get('submit')
        if (submitbutton == 'Search'):
            #     for i in range(0, len(names)):
            #         files = []
            #         th  = Parser(names[i], files)
            #         th.start()
            #         th.join()
            #         file = th.file
            #         # files = p.getFiles()
            #         x = Payment(names[i], file)
            #         simplelist.append(x)
            #
            newFiles = False
            simplelist = self.simplelist
            if len(simplelist) > 0:
                newFiles = True
            args = {'bank': simplelist[3].getName(), 'files': simplelist[3].getFiles(), 'newFiles': newFiles,
                    'button': submitbutton}
            return render(request, 'project/update_list.html', args)

        if submitbutton == "Parse":
            simplelist = self.simplelist
            # f = open("/home/mrx/Documents/choko-master/docs/demofile.txt", "w")
            # f.write(str(len(simplelist)))
            # logger.debug(len(simplelist))
            for i in range(0, len(simplelist)):
                files = simplelist[i].getFiles()
                name = simplelist[i].getName()
                for j in files:
                    if name == 'kaspi':
                        kaspi = KaspiParser(j)
                        kaspi.getParse()
                    if names[i] == 'nurbank':
                        nurbank = NurbankParser(j)
                        nurbank.getParse()
                    if names[i] == 'tourism':
                        tourism = ToursimParser(j)
                        tourism.getParse()
                    if names[i] == 'kazkom':
                        kazkom = KazkomParser(j)
                        kazkom.getParse()
        return redirect('/transaction')




def update_list(request):
    return render(request, 'project/update_list.html', {})

# return render(request, 'project/update_list.html', {})
