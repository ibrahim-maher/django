from django.urls import path
from .views.admin_views import (
    manage_tickets,
    edit_ticket,
    delete_ticket,
    create_registration,
    list_tickets,
    list_registrations,
    export_tickets_csv,
    export_registrations_csv,  # Added export registrations
    import_registrations_csv,  # Added import registrations
    manage_registration_fields,
    create_ticket,
    delete_registration_field,
    fetch_registration_fields,
    fetch_ticket_types,
    registration_detail,
    registration_edit,
    registration_delete,
)

app_name = 'registration'

urlpatterns = [
    # Ticket Management
    path('admin/tickets/<int:event_id>/', manage_tickets, name='admin_manage_tickets'),
    path('admin/tickets/edit/<int:ticket_id>/', edit_ticket, name='edit_ticket'),
    path('admin/tickets/delete/<int:ticket_id>/', delete_ticket, name='delete_ticket'),

    # List and Search Tickets
    path('admin/tickets/', list_tickets, name='admin_list_tickets'),

    # List and Search Registrations
    path('admin/registrations/', list_registrations, name='admin_list_registrations'),

    # Export CSV Routes
    path('admin/tickets/export/csv/', export_tickets_csv, name='export_tickets_csv'),
    path('admin/registrations/export/csv/', export_registrations_csv, name='export_registrations_csv'),  # New route

    # Import CSV Route
    path('admin/registrations/import/csv/', import_registrations_csv, name='import_registrations_csv'),  # New route

    # Create Ticket and Registration Routes
    path('create_ticket/', create_ticket, name='create_ticket'),
    path('register/', create_registration, name='create_registration'),

    # Registration Field Management
    path('admin/registration-fields/<int:event_id>/', manage_registration_fields,
         name='admin_manage_registration_fields'),
    path('admin/registration-fields/<int:event_id>/delete/<int:field_id>/', delete_registration_field,
         name='delete_registration_field'),

    path('events/<int:event_id>/registration-fields/', fetch_registration_fields, name='fetch_registration_fields'),
    path('events/<int:event_id>/ticket-types/', fetch_ticket_types, name='fetch_ticket_types'),

    path('registration/<int:registration_id>/', registration_detail, name='registration_detail'),
    path('registration/<int:registration_id>/edit/', registration_edit, name='registration_edit'),
    path('registration/<int:registration_id>/delete/', registration_delete, name='registration_delete'),
]
