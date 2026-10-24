from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.admission_list,
        name='admission_list'
    ),

    path(
        'apply/',
        views.admission_create,
        name='admission_create'
    ),

    path(
        '<int:pk>/',
        views.admission_detail,
        name='admission_detail'
    ),

    path(
        '<int:pk>/review/',
        views.admission_review,
        name='admission_review'
    ),
]