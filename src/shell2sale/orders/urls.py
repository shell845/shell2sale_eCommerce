from django.urls import path

from .views import (
    OrderListView,
    OrderDetailView,
    )

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('<order_id>/', OrderDetailView.as_view(), name='detail'),
]
