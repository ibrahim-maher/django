# management/views/report_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Report

@login_required
def reports_view(request):
    reports = Report.objects.all()
    return render(request, 'management/reports.html', {'reports': reports})