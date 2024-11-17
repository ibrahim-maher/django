import csv
import json
from datetime import datetime
from time import localtime
from django.shortcuts import redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from users.models import RoleChoices, CustomUser
from ..models import Ticket, RegistrationField, Registration
from ..forms import TicketForm, RegistrationFieldForm, DynamicRegistrationForm
from events.models import Event
from django.contrib.auth import get_user_model

# Utility function to check user roles


def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'


def is_event_manager(user):
    return user.is_authenticated and user.role == 'EVENT_MANAGER'


@login_required
def manage_tickets(request, event_id):
    """
    Admin can manage tickets (add, update, delete).
    """
    if not is_admin(request.user)  and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to manage tickets.")

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = event
            ticket.created_by = request.user
            ticket.save()
            return redirect('registration:admin_manage_tickets', event_id=event.id)
    else:
        form = TicketForm()

    tickets = Ticket.objects.filter(event=event)
    return render(request, 'registration/admin_manage_tickets.html', {
        'form': form, 'tickets': tickets, 'event': event
    })


@login_required
def  edit_ticket(request, ticket_id):
    """
    Admin can edit ticket details.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    event = ticket.event

    if not is_admin(request.user)  and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to edit tickets.")

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('registration:admin_manage_tickets', event_id=event.id)
    else:
        form = TicketForm(instance=ticket)

    return render(request, 'registration/admin_edit_ticket.html', {
        'form': form, 'ticket': ticket, 'event': event
    })


@login_required
def  delete_ticket(request, ticket_id):
    """
    Admin can delete a ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    event = ticket.event

    if not is_admin(request.user)  and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to delete tickets.")

    if request.method == 'POST':
        ticket.delete()
        return redirect('registration:admin_manage_tickets', event_id=event.id)

    return render(request, 'registration/admin_delete_ticket.html', {
        'ticket': ticket, 'event': event
    })


@login_required
def  list_tickets(request):
    """
    Admin can view all ticket types and search them by event name or ticket type.
    """
    if not is_admin(request.user) and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to view tickets.")

    search_query = request.GET.get('search', '').strip()
    tickets = Ticket.objects.select_related('event').all()

    if search_query:
        tickets = tickets.filter(
            Q(name__icontains=search_query) | Q(event__name__icontains=search_query)
        )

    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    rows = [
        {
            "cells": [
                ticket.name,
                f"${ticket.price:.2f}" if ticket.price else "Free",
                ticket.capacity,
                ticket.event.name if ticket.event else "N/A",
            ],
            "actions": [
                {
                    "url": reverse("registration:edit_ticket", args=[ticket.id]),
                    "class": "warning",
                    "icon": "la la-edit",
                    "label": "Edit",
                },
                {
                    "url": reverse("registration:delete_ticket", args=[ticket.id]),
                    "class": "danger",
                    "icon": "la la-trash",
                    "label": "Delete",
                },
            ],
        }
        for ticket in page_obj
    ]

    context = {
        "heading": "Ticket Types",
        "table_heading": "All Ticket Types",
        "columns": ["Name", "Price", "Capacity", "Event"],
        "rows": rows,
        "show_create_button": True,
        "create_action": reverse("registration:create_ticket"),
        "create_button_label": "Create Ticket",
        "search_action": reverse("registration:admin_list_tickets"),
        "search_placeholder": "Search Ticket Types...",
        "search_query": search_query,
        "paginator": paginator,
        "page_obj": page_obj,
    }

    return render(request, 'registration/admin_ticket_list.html', context)


@login_required
def create_ticket(request):
    """
    Allows admin to create a new ticket for a specific event.
    """
    if not is_admin(request.user)  and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to create tickets.")

    events = Event.objects.all()

    if request.method == 'POST':
        event_id = request.POST.get('event')
        selected_event = get_object_or_404(Event, id=event_id)

        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = selected_event
            ticket.created_by = request.user
            ticket.save()
            return redirect('registration:admin_list_tickets')
    else:
        form = TicketForm()

    return render(request, 'registration/create_ticket.html', {
        'form': form,
        'events': events
    })


@login_required

def list_registrations(request):
    """
    Admin can view all registrations and search them.
    """
    if not is_admin(request.user) and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to view registrations.")

    search_query = request.GET.get('search', '')
    registrations = Registration.objects.select_related('user', 'event', 'ticket_type').all()

    if search_query:
        registrations = registrations.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(event__name__icontains=search_query)
        )

    paginator = Paginator(registrations, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    rows = [
        {
            "cells": [
                registration.user.username,
                f"{registration.user.first_name} {registration.user.last_name}",
                registration.user.email,
                registration.user.title,
                registration.user.profile.phone_number if hasattr(registration.user, 'profile') else "N/A",
                registration.registered_at.strftime("%Y-%m-%d %H:%M"),
                registration.event.name,
                registration.ticket_type.name if registration.ticket_type else "N/A",
            ],
            "actions": [
                {
                    "url": reverse("registration:registration_detail", args=[registration.id]),
                    "class": "info",
                    "icon": "la la-eye",
                    "label": "View",
                },
                {
                    "url": reverse("registration:registration_edit", args=[registration.id]),
                    "class": "warning",
                    "icon": "la la-edit",
                    "label": "Edit",
                },
                {
                    "url": reverse("registration:registration_delete", args=[registration.id]),
                    "class": "danger",
                    "icon": "la la-trash",
                    "label": "Delete",
                },
            ],
        }
        for registration in page_obj
    ]

    context = {
        "heading": "Registrations",
        "table_heading": "Registration List",
        "columns": ["Username", "Full Name", "Email", "Title", "Phone", "Registration Date", "Event", "Ticket Type"],
        "rows": rows,
        "show_create_button": True,
        "create_action": reverse("registration:create_registration"),
        "create_button_label": "Create New Registration",
        "search_action": reverse("registration:admin_list_registrations"),
        "search_placeholder": "Search Registrations...",
        "search_query": search_query,
        "paginator": paginator,
        "page_obj": page_obj,
        # Import and Export buttons
        "show_export_button": True,
        "export_action": reverse("registration:export_registrations_csv"),
        "export_button_label": "Export CSV",
        "show_import_button": True,
        "import_action": reverse("registration:import_registrations_csv"),
        "import_button_label": "Import CSV",
    }

    return render(request, "registration/admin_registration_list.html", context)


import csv



def export_registrations_csv(request):
    if not request.user.is_admin and not request.user.is_event_manager:
        return HttpResponseForbidden("You don't have permission to export registrations.")

    registrations = Registration.objects.select_related('user', 'event', 'ticket_type').all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registrations.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Username",
        "First Name",
        "Last Name",
        "Email",
        "Title",
        "Phone",
        "Registration Date",
        "Event Name",
        "Ticket Type Name",
        "Registration Data"
    ])

    for registration in registrations:
        registration_data = registration.get_registration_data()  # Deserialize registration_data field
        writer.writerow([
            registration.user.username,
            registration.user.first_name,
            registration.user.last_name,
            registration.user.email,
            registration.user.title,
            registration.user.phone_number if registration.user.phone_number else "N/A",
            registration.registered_at.strftime("%Y-%m-%d %H:%M:%S"),
            registration.event.name,
            registration.ticket_type.name if registration.ticket_type else "N/A",
            json.dumps(registration_data),  # Serialize registration data back to JSON string
        ])

    return response



def import_registrations_csv(request):
    if not request.user.is_admin and not request.user.is_event_manager:
        return HttpResponseForbidden("You don't have permission to import registrations.")

    if request.method == 'POST' and 'csv_file' in request.FILES:
        file = request.FILES['csv_file']
        try:
            reader = csv.reader(file.read().decode('utf-8').splitlines())
            next(reader)  # Skip header row

            for row in reader:
                # Ensure the CSV includes all required fields
                try:
                    username, first_name, last_name, email, title, phone, registered_at, event_name, ticket_type_name, registration_data = row
                except ValueError:
                    messages.error(request, "CSV row does not have the correct number of fields.")
                    continue

                # Create or update the user
                user, created = CustomUser.objects.get_or_create(username=username, defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'title': title,
                    'phone_number': phone,
                    'role': RoleChoices.VISITOR,
                })


                # Lookup the event
                try:
                    event = Event.objects.get(name=event_name)
                except Event.DoesNotExist:
                    messages.error(request, f"Event '{event_name}' not found.")
                    continue

                # Lookup the ticket type
                ticket_type = Ticket.objects.filter(name=ticket_type_name, event=event).first()
                if not ticket_type:
                    messages.error(request, f"Ticket type '{ticket_type_name}' not found for event '{event_name}'.")
                    continue

                # Parse the registration data
                try:
                    parsed_registration_data = json.loads(registration_data)
                except json.JSONDecodeError:
                    messages.error(request, f"Invalid registration data format for user '{username}'.")
                    continue



                # Create the registration
                Registration.objects.create(
                    user=user,
                    event=event,
                    ticket_type=ticket_type,
                )

            messages.success(request, "Registrations imported successfully.")
        except Exception as e:
            messages.error(request, f"Error importing CSV: {e}")

    return redirect("registration:admin_list_registrations")

@login_required
def export_tickets_csv(request):
    """
    Export ticket types to a CSV file.
    """
    if not is_admin(request.user)  and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to export tickets.")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ticket_types.csv"'

    writer = csv.writer(response)
    writer.writerow(['Event Name', 'Ticket Type', 'Price', 'Capacity'])

    tickets = Ticket.objects.all()
    for ticket in tickets:
        writer.writerow([ticket.event.name, ticket.name, ticket.price, ticket.capacity])

    return response


@login_required
def create_registration(request):
    """
    Create a registration for an event.
    """
    if not is_admin(request.user)  and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to create registrations.")

    events = Event.objects.all()

    if request.method == 'POST':
        event_id = request.POST.get('event')
        selected_event = get_object_or_404(Event, id=event_id)

        form = DynamicRegistrationForm(event=selected_event, data=request.POST)
        if form.is_valid():
            registration_data = form.cleaned_data

            ticket_type_id = request.POST.get('ticket_type')
            ticket_type = get_object_or_404(Ticket, id=ticket_type_id, event=selected_event)

            Registration.objects.create(
                user=request.user,
                event=selected_event,
                ticket_type=ticket_type,
                registration_data=json.dumps(registration_data)
            )

            return redirect('registration:admin_list_registrations')
    else:
        form = DynamicRegistrationForm(event=None)

    return render(request, 'registration/create_registration.html', {
        'form': form,
        'events': events
    })



@login_required
def manage_registration_fields(request, event_id):
    """
    Admin can manage registration fields (add, delete).
    """
    if not is_admin(request.user)  and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to manage registration fields.")

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = RegistrationFieldForm(request.POST)
        if form.is_valid():
            field = form.save(commit=False)
            field.event = event
            field.created_by = request.user
            field.save()
            return redirect('registration:admin_manage_registration_fields', event_id=event.id)
    else:
        form = RegistrationFieldForm()

    fields = RegistrationField.objects.filter(event=event)
    return render(request, 'registration/admin_manage_registration_fields.html', {
        'form': form, 'fields': fields, 'event': event
    })



@login_required
def delete_registration_field(request, event_id, field_id):
    """
    Admin can delete a registration field.
    """
    if not is_admin(request.user)  and not is_event_manager(request.user):
        return HttpResponseForbidden("You don't have permission to delete registration fields.")

    event = get_object_or_404(Event, id=event_id)
    field = get_object_or_404(RegistrationField, id=field_id, event=event)

    if request.method == 'POST':
        field.delete()
        return redirect('registration:admin_manage_registration_fields', event_id=event.id)

    return render(request, 'registration/admin_delete_registration_field.html', {
        'field': field, 'event': event
    })

def registration_detail(request, registration_id):
    """
    View the details of a specific registration.
    """
    registration = get_object_or_404(Registration, id=registration_id)

    # Check permissions: Only admins, event managers, and the user who created the registration can view it
    if not (request.user.is_admin or request.user.is_event_manager or registration.user == request.user):
        return HttpResponseForbidden("You don't have permission to view this registration.")

    # Prepare the context for rendering
    context = {
        "registration": registration,
        "registration_data": registration.get_registration_data(),
    }

    return render(request, "registration/registration_detail.html", context)



@login_required
def registration_edit(request, registration_id):
    """
    Edit the details of a specific registration.
    """
    registration = get_object_or_404(Registration, id=registration_id)

    # Check permissions: Only admins, event managers, and the user who created the registration can edit it
    if not (request.user.is_admin or request.user.is_event_manager or registration.user == request.user):
        return HttpResponseForbidden("You don't have permission to edit this registration.")

    event = registration.event

    if request.method == "POST":
        form = DynamicRegistrationForm(event=event, data=request.POST, initial=registration.get_registration_data())
        if form.is_valid():
            registration_data = form.cleaned_data

            # Update ticket type if provided
            ticket_type_id = request.POST.get("ticket_type")
            if ticket_type_id:
                ticket_type = get_object_or_404(Ticket, id=ticket_type_id, event=event)
                registration.ticket_type = ticket_type

            # Save registration data
            registration.set_registration_data(registration_data)
            registration.save()

            return redirect("registration:registration_detail", registration_id=registration.id)
    else:
        form = DynamicRegistrationForm(event=event, initial=registration.get_registration_data())

    context = {
        "registration": registration,
        "form": form,
        "event": event,
    }
    return render(request, "registration/registration_edit.html", context)

def registration_delete(request, registration_id):
    """
    Deletes a specific registration.
    """
    registration = get_object_or_404(Registration, id=registration_id)

    # Check permissions: Only admins, event managers, or the user who created the registration can delete it
    if not (request.user.is_admin or request.user.is_event_manager or registration.user == request.user):
        return HttpResponseForbidden("You don't have permission to delete this registration.")

    if request.method == "POST":
        registration.delete()
        return redirect("registration:admin_list_registrations")  # Redirect to the list of registrations after deletion

    context = {
        "registration": registration,
    }
    return render(request, "registration/registration_delete.html", context)



@login_required
def fetch_ticket_types(request, event_id):
    """
    Fetch ticket types for a specific event.
    """
    # Check permissions
    if not (is_admin(request.user) or is_event_manager(request.user)):
        return JsonResponse({"error": "Permission denied"}, status=403)

    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event=event).values(
        "id", "name", "price", "capacity"
    )
    return JsonResponse(list(tickets), safe=False)


@login_required
def fetch_registration_fields(request, event_id):
    """
    Fetch registration fields for a specific event.
    """
    # Check permissions
    if not (is_admin(request.user) or is_event_manager(request.user)):
        return JsonResponse({"error": "Permission denied"}, status=403)

    event = get_object_or_404(Event, id=event_id)
    fields = RegistrationField.objects.filter(event=event).values(
        "field_name", "field_type", "is_required", "options"
    )
    return JsonResponse(list(fields), safe=False)