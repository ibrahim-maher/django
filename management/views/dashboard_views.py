# management/views/dashboard_views.py
import datetime
from time import timezone

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from registration.models import Registration, Ticket
from users.models import CustomUser, RoleChoices
from ..models import DashboardMetric
from events.models import Event, Venue, Category, Recurrence

from django.shortcuts import render
from events.models import Event, Venue, Category
@login_required

def dashboard_view(request):
    total_events = Event.objects.count()
    venues_count = Venue.objects.count()
    categories_count = Category.objects.count()
    registrations_count = Registration.objects.count()
    tickets_count = Ticket.objects.count()
    event_managers_count = CustomUser.objects.filter(role=RoleChoices.EVENT_MANAGER).count()
    ushers_count = CustomUser.objects.filter(role=RoleChoices.USHER).count()
    visitors_count = CustomUser.objects.filter(role=RoleChoices.VISITOR).count()

    # Update to match your registration model

    context = {
        'total_events': total_events,
        'venues_count': venues_count,
        'categories_count': categories_count,
        'registrations_count': registrations_count,
        'tickets_count': tickets_count,

        'event_managers_count': event_managers_count,
        'ushers_count': ushers_count,
        'visitors_count': visitors_count,
    }
    return render(request, 'management/dashboard.html', context)

@login_required
def event_manager_dashboard(request):
    metrics = DashboardMetric.objects.all()
    return render(request, 'management/dashboard.html', {'metrics': metrics, 'role': 'Event Manager'})