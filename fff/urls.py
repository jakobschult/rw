from django.urls import path
from . import views
from .views import AddOrderToEvent, order_intake_per_month

urlpatterns = [
    path('', views.index, name="index"),
    path('donations/', views.donations, name="donations"),
    path('donation/add', views.add_donation, name="add_donation"),
    path('collections', views.CollectionListView.as_view(), name="collections"),
    path('collection/add', views.add_collection, name='add_collection'),
    path('orders', views.OrderListView.as_view(), name="orders"),
    path('order/add/', views.add_order, name="add_order"),
    path('landingcontent/add', views.add_landing_content, name='add_landing_content'),
    path('order/<slug:hashed_id>/fulfill/', views.order_fulfill, name="order_fulfill"),
    path('order/<slug:hashed_id>/confirm/', views.order_confirm, name="order_confirm"),
    path('order/<slug:hashed_id>/invite/', views.order_invite, name="order_invite"),
    path('order/<slug:hashed_id>/decline/', views.order_decline, name="order_decline"),
    path('order/<slug:hashed_id>/remove/', views.order_remove, name="order_remove"),
    path('order/<slug:hashed_id>/plan/', views.order_plan, name="order_plan"),
    path('order/<int:order_id>/', views.order_detail, name="order_details"),
    path('order/intake/month/', order_intake_per_month, name="order_intake_per_month"),
    path('volunteer/<int:volunteer_id>/events', views.volunteer_events, name="volunteer_events"),
    path('events/', views.events, name="events"),
    path('event/add/', views.add_event, name="add_event"),
    path('event/<int:event_id>/', views.event, name="event_detail"),
    path('event/<int:event_id>/inviteall', views.event_invite_all, name="event_invite_all"),
    path('event/<int:event_id>/addorder/', views.add_order_to_event, name="add_order_to_event"),
    path('event/<int:event_id>/delete/', views.event_delete, name="event_delete"),
    path('bike/<int:bike_id>/remove', views.bike_remove, name="bike_remove"),
    path('website', views.website, name="website"),
    path('website/team', views.website_team, name="website_team"),
    path('website/order', views.website_order, name="website_order"),
    path('website/news', views.website_news, name="website_news"),
    path('website/donate', views.website_donate, name="website_donate"),
    path('website/bikedonation', views.website_bikedonate, name="website_bikedonate"),

]
