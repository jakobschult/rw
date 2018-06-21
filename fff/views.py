from .forms import EventForm, ContactForm, BikeDonationForm, CollectionForm, LandingContentForm
from .models import Order, Event, Bike, User, LandingContent, BikeDonation, Collection
from datetime import date
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import View
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Sum, Count, Q
from django.utils.translation import gettext
from django.contrib import messages
from django.views.generic import ListView


class BikeDonationListView(ListView):
    model = BikeDonation
    template_name = "donations.html"

    def get_queryset(self):
        donations = BikeDonation.objects.values('date_input', 'zip', 'latest_pickup', 'bike_count', 'status')
        return donations


def donations(request):
    context = {
        'donations_values': BikeDonation.objects.values('date_input', 'zip', 'latest_pickup', 'bike_count', 'status'),
        'donations': BikeDonation.objects.all()
    }
    return render(request, 'donations.html', context)


class OrderListView(ListView):
    model = Order
    template_name = "orders.html"

    def get_queryset(self):
        orders = Order.objects.values('name', 'bikes', 'date_input', 'status', 'event')
        return orders


class CollectionListView(ListView):
    model = Order
    template_name = "collections.html"

    def get_queryset(self):
        collections = Collection.objects.values('date', 'capacity')
        return collections


def website(request):
    contact_form = ContactForm(request.POST or None)

    landing_content = LandingContent.objects.get(pk=LandingContent.objects.count())
    if contact_form.is_valid():
        subject = gettext('contact_form_email_subject')
        name = contact_form.cleaned_data['name']
        email = contact_form.cleaned_data['email']
        phone = contact_form.cleaned_data['phone']
        form_message = contact_form.cleaned_data['message']
        to = ['jakobschult@yahoo.de']

        message = "<html>" \
                  "Hello, <br>" \
                  "<br>" \
                  "folgende Nachricht wurde über die Internetseite an uns gesendet:<br><br>" \
                  "Von: " + name + "<br>" \
                                   "Email: " + email + "<br>" \
                                                       "Phone: " + phone + "<br>" \
                                                                           "Nachricht: " + form_message

        email_message = EmailMultiAlternatives(subject=subject, from_email="info@rueckenwind.berlin", to=to,
                                               headers={'Reply-To': email})
        email_message.attach_alternative(message, "text/html")
        email_message.send()
        messages.success(request, 'Form submission successful')

        pass

    context = {
        'contact_form': contact_form,
        'landing_content': landing_content,
    }
    return render(request, 'website/index.html', context)


def website_order(request):
    if (request.method == 'POST'):
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        bikes = request.POST['bikes']
        note = request.POST['note']
        order = Order(name=name,
                      email=email,
                      phone=phone,
                      bikes=bikes,
                      note=note, )
        order.status = "ORDERED"
        order.date_input = date.today()
        order.save()
        return redirect('website_order')
    else:
        return render(request, 'website/bike_order.html')


def add_landing_content(request):
    landing_content_form = LandingContentForm(request.POST or None)

    if landing_content_form.is_valid():
        landing_content_form.save()

    context = {
        'landing_content_form': landing_content_form,
    }
    return render(request, 'add_landing_content.html', context)


def website_bikedonate(request):
    bike_donation_form = BikeDonationForm(request.POST or None)

    if bike_donation_form.is_valid():
        bike_donation = bike_donation_form.save(commit=False)
        bike_donation.geocode()
        bike_donation.date_input = date.today()
        bike_donation.save()
        messages.success(request, gettext('bikedonation_submit_success_message'))

    context = {
        'bike_donation_form': bike_donation_form,
    }
    return render(request, 'website/bike_donation.html', context)


def add_donation(request):
    bike_donation_form = BikeDonationForm(request.POST or None)

    if bike_donation_form.is_valid():
        bike_donation = bike_donation_form.save(commit=False)
        bike_donation.geocode()
        bike_donation.date_input = date.today()
        bike_donation.save()
        return redirect('donations')
    context = {
        'bike_donation_form': bike_donation_form,
    }
    return render(request, 'add_donation.html', context)


def website_team(request):
    context = {

    }
    return render(request, 'website/team.html', context)


def website_news(request):
    context = {

    }
    return render(request, 'website/news.html', context)


def website_donate(request):
    context = {

    }
    return redirect(
        "https://www.betterplace.org/de/projects/61457-jeden-tag-ein-fahrrad-fur-gefluchtete-unser-ziel-in-2018/")


def events(request):
    events = Event.objects.filter(date__gte=date.today()).order_by('date')
    past_events = Event.objects.filter(date__lt=date.today()).order_by('date')
    context = {
        'events': events,
        'past_events': past_events,
    }
    return render(request, 'events.html', context)


def bike_remove(request, bike_id):
    bike = Bike.objects.get(id=bike_id)
    order_hashed_id = bike.order.hashed_id
    bike.remove_order()
    return redirect("/fff/order/" + order_hashed_id + "/fulfill")


def volunteer_events(request, volunteer_id):
    if (request.method == 'POST'):
        volunteer = User.objects.get(id=volunteer_id)
        event = Event.objects.get(id=request.POST['event_id'])
        if request.POST['operation'] == "remove":
            event.volunteers.remove(volunteer)
        elif request.POST['operation'] == "add":
            event.volunteers.add(volunteer)
        event.save()
    events = list(Event.objects.order_by('date'))
    volunteer_events = Event.objects.filter(volunteers__id=volunteer_id).extra(order_by=['date'])

    for volunteer_event in volunteer_events:
        events.remove(volunteer_event)

    context = {
        'events': events,
        'volunteer_events': volunteer_events,
        'volunteer_id': volunteer_id,
    }
    return render(request, 'volunteer_events.html', context)


class AddOrderToEvent(View):
    def get(self, request, *args, **kwargs):
        event = Event.objects.get(id=kwargs["event_id"])
        orders = Order.objects.order_by('date_input')
        context = {
            "orders": orders,
            "event": event,
        }
        return render(request, "add_order_to_event.html", context)

    def post(self, request, *args, **kwargs):
        for order_id in request.POST.getlist("orders"):
            order = Order.objects.get(id=order_id)
            order.plan(event)
            order.save()
        event.save()
        return redirect("/fff/event/" + str(kwargs["event_id"]))  # warum muss ich das hier machen


def order_intake_per_month(request, *args, **kwargs):
    orders = Order.objects \
        .annotate(month=ExtractMonth('date_input'),
                  year=ExtractYear('date_input')) \
        .values('month', 'year') \
        .annotate(count=Count('pk')) \
        .annotate(bikes=Sum('bikes'))

    labels = []
    orders_count = []
    bikes_count = []
    for order in orders:
        month = str(order['month'])
        year = str(order['year'])
        order_count = order['count']
        bike_count = order['bikes']

        labels.append(year + "-" + month)
        orders_count.append(order_count)
        bikes_count.append(bike_count)

    data = {"labels": labels,
            "orders_count": orders_count,
            "bikes_count": bikes_count,
            }

    return JsonResponse(data, safe=False)  # that returns a http response


def add_order_to_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if (request.method == 'POST'):
        for order_id in request.POST.getlist("orders"):
            order = Order.objects.get(id=order_id)
            order.plan(event)
            order.save()
        event.save()
        return redirect("/fff/event/" + str(event_id))  # warum muss ich das hier machen
    orders = Order.objects.filter(
        Q(status="ORDERED") | Q(status="PLANNED") | Q(status="INVITED") | Q(status="DECLINED")).order_by('date_input')
    context = {
        "orders": orders,
        "event": event,
    }
    return render(request, "add_order_to_event.html", context)


def index(request):
    if (request.method == 'POST'):
        event_id = request.POST['event_id']
        event = Event.objects.get(id=event_id)
        for order_id in request.POST.getlist("orders"):
            order = Order.objects.get(id=order_id)
            order.plan(event)
            order.save()
        event.save()
        return redirect('/fff/event/' + event_id)

    orders = Order.objects.all()
    events = Event.objects.all()
    context = {
        'orders': orders,
        'events': events,
    }
    return render(request, 'index.html', context)


def order_confirm(request, hashed_id):
    order = Order.objects.filter(hashed_id=hashed_id)
    event_id = 0
    for o in order:
        event_id = o.event.pk
        o.confirm()
        o.save()
    context = {
        'order': order,
    }
    return render(request, 'index.html', context)


def order_invite(request, hashed_id):
    order = Order.objects.filter(hashed_id=hashed_id)
    event_id = 0
    for o in order:
        event_id = o.event.pk
        o.invite()
        o.save()
    return redirect('/fff/event/' + str(event_id))


def order_decline(request, hashed_id):
    order = Order.objects.filter(hashed_id=hashed_id)
    event_id = 0
    for o in order:
        event_id = o.event.pk
        o.decline()
        o.save()
    return redirect('/fff/event/' + str(event_id))


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {
        'order': order
    }
    return render(request, 'details.html', context)


def order_fulfill(request, hashed_id):
    order = Order.objects.get(hashed_id=hashed_id)

    if request.method == "POST":
        bike = Bike()
        bike.manufacturer = request.POST.get('bike_manufacturer')
        bike.frame_number = request.POST.get('bike_frame_number')
        bike.color = request.POST.get('bike_color')

        order = Order.objects.get(hashed_id=hashed_id)
        order.fulfill()
        order.save()
        bike.order = order
        bike.save()
        bikes = Bike.objects.filter(order=order)
        context = {
            'order': order,
            'bikes': bikes,
        }
        return render(request, 'order_fulfill.html', context)
    else:
        bikes = Bike.objects.filter(order=order)
        context = {
            'order': order,
            'bikes': bikes,
        }
        return render(request, 'order_fulfill.html', context)


def order_plan(request, hashed_id):
    order = Order.objects.get(hashed_id=hashed_id)
    current_event_id = order.event.pk
    events = Event.objects.order_by('date')

    if request.method == "POST":
        selected_event = Event.objects.get(pk=request.POST["eventSelect"])
        order.status = "PLANNED"
        order.event = selected_event
        order.save()
        return redirect('/fff/event/' + request.POST["eventSelect"])

    context = {

        "hashed_id": hashed_id,
        "current_event_id": current_event_id,
        "events": events,
    }

    return render(request, "order_plan.html", context)


def order_remove(request, hashed_id):
    order = Order.objects.get(hashed_id=hashed_id)  #
    event_id = order.event.pk
    order.event = None

    #  update status information
    if order.status == "PLANNED":
        order.status = "ORDERED"
    if order.status == "DECLINED":
        order.status = "DECLINED"
    order.save()
    return redirect("/fff/event/" + str(event_id))


def add_order(request):
    if (request.method == 'POST'):
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        bikes = request.POST['bikes']
        note = request.POST['note']
        order = Order(name=name,
                      email=email,
                      phone=phone,
                      bikes=bikes,
                      note=note, )
        order.status = "ORDERED"
        order.date_input = date.today()
        order.save()
        messages.success(request, "Thank you for the registration! Please check your mail and reply!")
        return redirect('/fff/order/add')
    else:
        return render(request, 'add_order.html')


def add_event(request):
    add_event_form = EventForm(request.POST or None)

    if add_event_form.is_valid():
        new_event = add_event_form.save()
        return redirect('/fff/event/' + str(new_event.pk))

    context = {
        'event_form': add_event_form,
    }
    return render(request, 'add_event.html', context)


def add_collection(request):
    add_collection_form = CollectionForm(request.POST or None)

    if add_collection_form.is_valid():
        new_collection = add_collection_form.save()
        return redirect('/fff/collections')

    context = {
        'collection_form': add_collection_form,
    }
    return render(request, 'add_collection.html', context)


def event_delete(request, event_id):
    event = Event.objects.get(pk=event_id)
    event.delete()
    return redirect('/fff/events/')


def event_invite_all(request, event_id):
    event = Event.objects.get(pk=event_id)
    for order in Order.objects.filter(event=event):
        order.invite()
        order.save()
    return redirect('/fff/event/' + str(event_id))


@login_required
def event(request, event_id):
    event = Event.objects.get(id=event_id)
    if (request.method == 'POST'):
        for volunteer_id in request.POST.getlist("volunteers"):
            volunteer = User.objects.get(id=volunteer_id);
            event.volunteers.add(volunteer)
            event.save()
        return redirect('/fff/event/' + event_id)
    else:
        orders = Order.objects.filter(event=event)
        volunteers = User.objects.all
        event_volunteers = event.volunteers.all()
        context = {
            'orders': orders,
            'ordercount': orders.count(),
            'event': event,
            'volunteers': volunteers,
            'event_volunteers': event_volunteers,
        }
        return render(request, 'event.html', context)
