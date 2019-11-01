"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views, authenticate
from .views import *


app_name = 'parameter-manager'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', UserFormView.as_view(), name='register'),
    path('', include('django.contrib.auth.urls')),
    path('add-database', add_database, name='add-database'),

    # Views ---------------------------------------------------------------------
    # path('set-optimal-values', OptimalFormView.as_view(), name='set-optimal-values'),
    path('set-optimal-values', set_optimal_values, name='set-optimal-values'),
    path('update-optimal-values', update_optimal_values, name='update-optimal-values'),
    path('show-database', show_database, name='show-database'),
    path('dashboard', show_dashboard, name='dashboard'),

    # Get From Database ---------------------------------------------------------
    path('get-database', get_database, name="get-database"),
    path('show-importants', get_importants, name='get-importants'),
    path('get-history', get_history, name='get-history'),
    path('get-io-mem', get_iomem, name='get-io-mem'),
    path('certain-data', get_certain_data, name='certain-data'),
    path('certain-data-form', certain_data_form, name='certain-data-form'),
    path('filter-by-time', filter_by_time, name='filter-by-time'),
    path('filter-by-value', filter_by_value, name='filter-by-value'),

    # Update database -----------------------------------------------------------
    path('set-checks', set_checks, name='set-checks'),
    path('refresh-db', refresh_db, name='check-for-updates'),
    path('delete-important', delete_important, name='delete-important'),
    path('make-graph', make_graph, name='make-graph'),

    # Try smth
    path('try-smth', try_smth, name='try-smth')



]


