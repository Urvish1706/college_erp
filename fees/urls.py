from django.urls import path
from .views import (
    fee_list,
    fee_detail,
    fee_create,
    fee_update,
    fee_delete,
    payment_create,
    payment_delete,
    payment_history,
    receipt_view,
    student_fees,
)

urlpatterns = [
    path("", fee_list, name="fee_index"),
    path("list/", fee_list, name="fee_list"),
    path("fees-list/", fee_list, name="fees_list"),
    path("my-fees/", student_fees, name="student_fees"),
    path("student/", student_fees),
    path("create/", fee_create, name="fee_create"),
    path("<int:pk>/", fee_detail, name="fee_detail"),
    path("<int:pk>/edit/", fee_update, name="fee_update"),
    path("<int:pk>/delete/", fee_delete, name="fee_delete"),
    path("<int:fee_pk>/payment/create/", payment_create, name="payment_create"),
    path("<int:fee_pk>/payments/", payment_history, name="payment_history"),
    path("payment/<int:pk>/delete/", payment_delete, name="payment_delete"),
    path("receipt/<int:payment_pk>/", receipt_view, name="receipt_view"),
]
