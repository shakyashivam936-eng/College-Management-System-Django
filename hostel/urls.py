from django.urls import path

from . import views


app_name = "hostel"


urlpatterns = [

    path(
        "",
        views.hostel_dashboard,
        name="dashboard"
    ),

    path(
        "hostels/",
        views.hostel_list,
        name="hostel_list"
    ),

    path(
        "hostels/create/",
        views.hostel_create,
        name="hostel_create"
    ),

    path(
        "rooms/",
        views.room_list,
        name="room_list"
    ),

    path(
        "rooms/create/",
        views.room_create,
        name="room_create"
    ),

    path(
        "beds/",
        views.bed_list,
        name="bed_list"
    ),

    path(
        "beds/create/",
        views.bed_create,
        name="bed_create"
    ),

    path(
        "allocations/create/",
        views.allocation_create,
        name="allocation_create"
    ),

    path(
        "allocations/<int:pk>/",
        views.allocation_detail,
        name="allocation_detail"
    ),

    path(
        "allocations/<int:pk>/release/",
        views.release_allocation,
        name="release_allocation"
    ),

    path(
        "fees/<int:pk>/pay/",
        views.pay_hostel_fee,
        name="pay_hostel_fee"
    ),

    path(
    "fees/<int:pk>/payment/",
    views.hostel_fee_payment,
    name="hostel_fee_payment"
),

path(
    "fees/payment/<int:pk>/receipt/",
    views.hostel_fee_receipt,
    name="hostel_fee_receipt"
),
]
