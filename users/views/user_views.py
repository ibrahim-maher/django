# users/views/user_views.py
import csv

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponse
from rest_framework.reverse import reverse

from ..models import CustomUser, RoleChoices
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout

from ..forms import CustomUserCreationForm, EditProfileForm
from ..models import CustomUser
from django.shortcuts import render


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('users:role_based_dashboard')  # Prefix with 'users' if necessary
    return render(request, 'users/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})




@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form, 'user': request.user})
@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})
def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect after logout

@login_required
def role_based_dashboard(request):
    user = request.user
    if user.is_admin:
        return redirect('management:dashboard')  # Redirect to admin dashboard
    elif user.is_event_manager:
        return redirect('management:event_manager_dashboard')
    elif user.is_usher:
        return redirect('checkin:checkin')
    elif user.is_visitor:
        return redirect('users:profile')
    else:
        return redirect('home')  # Fallback if no role is matched


def is_admin(user):
    return user.role == RoleChoices.ADMIN
def is_event_manager(user):
    return  user.role == RoleChoices.EVENT_MANAGER


@login_required
def user_list_view(request, role=None, role_label=None):
    """
    List users by role with search and pagination.
    """
    if not (is_admin(request.user)):
        return HttpResponseForbidden("You don't have permission to view this page.")

    # Set default role label if not provided
    if role_label is None:
        role_label = role.capitalize() if role else "User"

    search_query = request.GET.get("search", "")
    users = CustomUser.objects.all() if role is None else CustomUser.objects.filter(role=role)

    if search_query:
        users = users.filter(username__icontains=search_query)

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Base URL for maintaining role in paths
    base_url = f"/users/{role}/" if role else "/users/"

    # Prepare rows for the table
    rows = [
        {
            "cells": [
                user.username,
                user.email,
                user.phone_number or "N/A",
                user.date_of_birth.strftime("%Y-%m-%d") if user.date_of_birth else "N/A",
                user.address or "N/A",
            ],
            "actions": [
                {
                    "url": reverse("users:edit_user", kwargs={"user_id": user.id}),
                    "class": "warning",
                    "icon": "la la-edit",
                    "label": "Edit",
                },
                {
                    "url": reverse("users:delete_user", kwargs={"user_id": user.id}),
                    "class": "danger",
                    "icon": "la la-trash",
                    "label": "Delete",
                },
            ],
        }
        for user in page_obj
    ]

    # Context for rendering
    context = {
        "heading": f"{role_label}s",
        "table_heading": f"All {role_label}s",
        "columns": ["Username", "Email", "Phone Number", "Date of Birth", "Address"],
        "rows": rows,
        "show_create_button": True,
        "create_action": reverse("users:create_user",kwargs={"role":role}),  # Updated namespace
        "create_button_label": f"Create {role_label}",
        "search_action": request.path,  # Maintain current path for searching
        "search_placeholder": f"Search {role_label}s...",
        "search_query": search_query,
        "show_export_button": True,
        "export_action": (
            reverse("users:export_users_by_role", kwargs={"role": role})
            if role
            else reverse("users:export_users")
        ),
        "export_button_label": "Export CSV",
        "show_import_button": True,
        "import_action": (
            reverse("users:import_users_by_role", kwargs={"role": role})
            if role
            else reverse("users:import_users")
        ),
        "import_button_label": "Import CSV",
        "paginator": paginator,
        "page_obj": page_obj,
    }

    return render(request, "users/user_list.html", context)


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.hashers import make_password



def create_user(request, role=None):
    """
    View function to create a new user.
    If role is specified, it will create a user with that role.
    Only admins can create users with roles other than VISITOR.
    """
    # Check if user has permission to create users
    if not request.user.is_authenticated or not request.user.is_admin:
        return HttpResponseForbidden("You don't have permission to create users.")

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            try:
                # Create user but don't save yet
                user = form.save(commit=False)

                # If role is specified in URL, override form role
                if role:
                    # Validate that the role is valid
                    if role not in dict(RoleChoices.choices):
                        messages.error(request, "Invalid role specified.")
                        return redirect('users:user_list')
                    user.role = role

                # Additional validation for role creation permissions
                if user.role in [RoleChoices.ADMIN, RoleChoices.EVENT_MANAGER, RoleChoices.USHER]:
                    if not request.user.is_admin:
                        messages.error(request, "You don't have permission to create users with this role.")
                        return redirect('users:user_list')

                # Save the user
                user.save()

                messages.success(
                    request,
                    f"Successfully created {user.get_role_display()} user: {user.username}"
                )

                # Redirect based on role
                if role:
                    return redirect('users:user_list_by_role', role=role)
                return redirect('users:user_list')

            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")
                return redirect('users:user_list')
    else:
        # For GET request, create empty form
        initial_data = {}
        if role:
            if role not in dict(RoleChoices.choices):
                messages.error(request, "Invalid role specified.")
                return redirect('users:user_list')
            initial_data['role'] = role

        form = CustomUserCreationForm(initial=initial_data)

    context = {
        'form': form,
        'heading': f"Create {'User' if not role else role.capitalize()}",
        'submit_label': 'Create User',
        'cancel_url': reverse('users:user_list_by_role', kwargs={'role': role}) if role else reverse('users:user_list'),
    }

    return render(request, 'users/user_form.html', context)


@login_required
def edit_user(request, user_id):
    """
    Edit an existing user.
    """
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to edit users.")

    user_to_edit = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            response = user_list_view(request, user_to_edit.role)
            return response
    else:
        form = EditProfileForm(instance=user_to_edit)

    return render(request, "users/edit_user.html", {"form": form, "user_to_edit": user_to_edit})


@login_required
def delete_user(request, user_id):
    """
    Delete a user.
    """
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to delete users.")

    user_to_delete = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user_to_delete.delete()
        response = user_list_view(request, user_to_delete.role)

        return response  # Redirect to user list view

    return render(request, "users/delete_user.html", {"user_to_delete": user_to_delete})


@login_required
def import_users_csv(request, role=None):
    """
    Import users from a CSV file.
    """
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to import users.")

    if request.method == "POST" and "csv_file" in request.FILES:
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            return render(request, "users/user_list.html", {"error_message": "Please upload a valid CSV file."})

        file_data = csv_file.read().decode("utf-8").splitlines()
        csv_reader = csv.reader(file_data)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            try:
                username, email, csv_role, phone_number, address, date_of_birth = row

                if role and csv_role.upper() != role.upper():
                    continue  # Skip roles that don't match

                CustomUser.objects.update_or_create(
                    username=username.strip(),
                    defaults={
                        "email": email.strip(),
                        "role": csv_role.strip().upper(),
                        "phone_number": phone_number.strip(),
                        "address": address.strip(),
                        "date_of_birth": date_of_birth.strip(),
                    },
                )
            except Exception as e:
                return render(request, "users/user_list.html", {"error_message": f"Error processing row: {str(e)}"})

        return redirect("export_users")

    return redirect("export_users")


@login_required
def export_users_csv(request, role=None):
    """
    Export users to a CSV file.
    """
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to export users.")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="users_{role or "all"}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Username", "Email", "Role", "Phone Number", "Address", "Date of Birth"])

    users = CustomUser.objects.filter(role=role.upper()) if role else CustomUser.objects.all()

    for user in users:
        writer.writerow([user.username, user.email, user.role, user.phone_number, user.address, user.date_of_birth])

    return response