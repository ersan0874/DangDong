from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Home
    path('', views.home_view, name='home'),

    # Trips
    path('trip/new/', views.create_trip_view, name='create_trip'),
    path('trip/<int:trip_id>/', views.trip_detail_view, name='trip_detail'),
    path('trip/<int:trip_id>/add_participant/', views.add_participant_view, name='add_participant'),
    path('trip/<int:trip_id>/add_expense/', views.add_expense_view, name='add_expense'),
]
