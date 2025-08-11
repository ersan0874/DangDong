from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Trip, Expense
from .forms import TripForm, AddParticipantForm, ExpenseForm
from .services import calculate_trip_balances

# --- Authentication Views ---
def register_view(request):
    if request.user.is_authenticated: return redirect('main:home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:login')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: return redirect('main:home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                login(request, user)
                return redirect('main:home')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('main:login')

# --- Trip & Expense Views ---
@login_required
def home_view(request):
    user_trips = Trip.objects.filter(participants=request.user).order_by('-created_at')
    return render(request, 'main/home.html', {'trips': user_trips})

@login_required
def create_trip_view(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.organizer = request.user
            trip.save()
            trip.participants.add(request.user)
            return redirect('main:trip_detail', trip_id=trip.id)
    else:
        form = TripForm()
    return render(request, 'main/create_trip.html', {'form': form})

@login_required
def trip_detail_view(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, participants=request.user)
    expenses = trip.expenses.all().order_by('-date')

    # Forms
    add_participant_form = AddParticipantForm()
    expense_form = ExpenseForm(trip=trip)

    # Calculations
    balances, transactions, category_summary = calculate_trip_balances(trip)
    total_cost = sum(e.amount for e in expenses)

    return render(request, 'main/trip_detail.html', {
        'trip': trip,
        'expenses': expenses,
        'total_cost': total_cost,
        'add_participant_form': add_participant_form,
        'expense_form': expense_form,
        'balances': balances.items(),
        'transactions': transactions,
        'category_summary': category_summary.items(),
    })

@login_required
def add_participant_view(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, organizer=request.user)
    if request.method == 'POST':
        form = AddParticipantForm(request.POST)
        if form.is_valid():
            user_to_add = User.objects.get(email=form.cleaned_data['email'])
            trip.participants.add(user_to_add)
    return redirect('main:trip_detail', trip_id=trip.id)

@login_required
def add_expense_view(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, participants=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, trip=trip)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.trip = trip
            expense.save()
            # The form's save_m2m() method needs to be called for ManyToManyFields
            form.save_m2m()
            # Pre-select all participants if split_with is empty
            if not expense.split_with.exists():
                expense.split_with.set(trip.participants.all())
    return redirect('main:trip_detail', trip_id=trip.id)
