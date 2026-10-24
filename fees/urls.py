from django.urls import path

from . import views


app_name = "fees"


urlpatterns = [

    path(
        "",
        views.fee_structure_list,
        name="fee_structure_list"
    ),

    path(
        "create/",
        views.fee_structure_create,
        name="fee_structure_create"
    ),

    path(
        "assign/",
        views.student_fee_create,
        name="student_fee_create"
    ),

    path(
        "student/<int:pk>/",
        views.student_fee_detail,
        name="student_fee_detail"
    ),

    path(
        "student/<int:pk>/payment/",
        views.make_payment,
        name="make_payment"
    ),

    path(
        "payment/<int:pk>/receipt/",
        views.payment_receipt,
        name="payment_receipt"
    ),
     path(
        'dashboard/',
        views.fees_dashboard,
        name='dashboard'
    ),
]