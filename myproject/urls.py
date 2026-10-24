"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


def home(request):
    return redirect('login')


urlpatterns = [

     path("dashboard/", include("dashboard.urls")),
    path('academics/', include('academics.urls')),
     
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('student/', include('students.urls')),
    path('students/', include('students.urls')),
    path('admissions/', include('admissions.urls')),
    path('fees/', include('fees.urls')),
    path(
        "hostel/",
        include("hostel.urls")
    ),
    path(
        "exams/",
        include("exams.urls")
    ),
    path(
        "exams_result_dashboard/",
        RedirectView.as_view(pattern_name="exams:exam_list"),
        name="legacy_exam_dashboard"
    ),
    path(
        "exams_result_dashboard",
        RedirectView.as_view(pattern_name="exams:exam_list"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
