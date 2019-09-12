"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
import os

from django.urls import include, path


urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("companies/", include("companies.urls")),
    path("activities/", include("activities.urls")),
]

# We add the api prefix within development because
# we can't re-route the url's easily with runserver
if bool(int(os.environ.get("DEVELOPMENT", False))):
    urlpatterns = [path("api/", include(urlpatterns))]
