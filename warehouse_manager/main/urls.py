from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/',
         LoginView.as_view(template_name='main/login.html',
                           next_page='home'),
         name='login'),
    path('warehouse/<slug:wh_slug>/', WarehouseView.as_view(), name='warehouse'),
    # path('warehouse/<slug:wh_slug>/<slug:status_slug>', StatusSelected.as_view(), name='warehouse_status'),
    path('warehouse/', WarehouseCommonPage.as_view(), name='warehouses'),
    path('warehouse/<slug:wh_slug>/ticket/<int:tick_id>', TicketsView.as_view(), name='ticket'),
    path('warehouse/<slug:wh_slug>/ticket/<int:tick_id>/reply/',
         WarehouseReply.as_view(),
         name='reply'
         ),
    path('create-trip', CreateTicket.as_view(), name='trip_creation'),
    path('create-trip/<str:manifest>', CreateTicket.as_view(), name='trip_creation'),
    path('logout', logout_user, name='logout'),
]

