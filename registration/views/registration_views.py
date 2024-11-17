from django.shortcuts import render, get_object_or_404, redirect
from ..models import Ticket, TicketType, Registration
from events.models import Event
from ..forms import DynamicRegistrationForm
from django.contrib.auth.decorators import login_required

@login_required
def register(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ticket_types = TicketType.objects.filter(event=event)

    if request.method == 'POST':
        form = DynamicRegistrationForm(event, request.POST)
        if form.is_valid():
            registration_data = form.cleaned_data
            ticket_type = registration_data.pop('ticket_type')
            ticket = Ticket.objects.create(
                event=event,
                user=request.user,
                ticket_type=ticket_type
            )
            Registration.objects.create(
                event=event,
                user=request.user,
                ticket=ticket,
                registration_data=registration_data
            )
            return redirect('registration:success')
    else:
        form = DynamicRegistrationForm(event)
    return render(request, 'registration/register.html', {'form': form, 'event': event})
