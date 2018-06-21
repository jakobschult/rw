from django.db import models
import datetime
import hashlib
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMultiAlternatives
from .keys import *
from datetime import date
import googlemaps
from datetime import datetime

class Collection(models.Model):
    date = models.DateField(blank=True, null=True, help_text="When do you want to collect the bicycles")
    capacity = models.IntegerField(blank=True, null=True, help_text="How many bikes can be collected?")


class BikeDonation(models.Model):
    date_input = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50,blank=True, null=True)
    address = models.CharField(max_length=50)
    zip = models.CharField(max_length=50)
    latest_pickup = models.DateField(max_length=50,blank=True, null=True)
    bike_count = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True, max_length=300)
    status = models.TextField(blank=True, null=True)
    collection = models.ForeignKey(Collection, blank=True, null=True, on_delete=models.SET_NULL)
    latitude = models.CharField(max_length=13, blank=True,null=True)
    longitude = models.CharField(max_length=13, blank=True,null=True)

    def geocode(self):
        gmaps = googlemaps.Client(key='AIzaSyCqGX-4MXal5Pey0KXubD7U1tL32np940I')
        # Geocoding an address
        geocode_result = gmaps.geocode(self.address + ", " + self.zip)
        print(geocode_result)
        location = geocode_result[0]['geometry']['location']
        print(location)
        self.latitude = location['lat']
        self.longitude = location['lng']


    def save(self, *args, **kwargs):
        self.geocode()
        super(BikeDonation, self).save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return self.name


class LandingContent(models.Model):
    text = models.CharField(help_text="What should be displayed in the box on the homepage?", max_length=50)
    link = models.URLField(help_text="What should be displayed in the box on the homepage?")

    def __str__(self):
        return self.text


class User(AbstractUser):
    phone = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Event(models.Model):
    date = models.DateField(blank=True, null=True, help_text="When do you want to repair?")
    capacity = models.IntegerField(blank=True, null=True, help_text="How many bikes can be repaired?")
    volunteers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return "" + str(self.date)

    def get_planned_bikes(self):
        result = 0
        for order in self.order_set.all():
            result = result + int(order.bikes)
        return result

    def get_all_volunteers(self):
        result = ""
        for volunteer in self.volunteers.all():
            result = result + "    " + volunteer.username
        return result


class Order(models.Model):
    name = models.CharField(max_length=100)
    bikes = models.IntegerField(help_text="How many bikes are we talking about", null=True)
    bikes_fulfilled = models.IntegerField(blank=True, null=True)
    date_input = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    note = models.CharField(max_length=300, blank=True, null=True)
    date_invited = models.DateField(blank=True, null=True)
    date_answered = models.DateField(blank=True, null=True)
    date_repaired = models.DateField(blank=True, null=True)
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=30, blank=True, null=True)
    hashed_id = models.CharField(max_length=256, blank=True, null=True)

    def get_field_map(self):
        return {'name': self.name, 'name': self.name}

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.hashed_id = hashlib.sha256(str(self.pk).encode("utf-8")).hexdigest()
        super(Order, self).save(*args, **kwargs)  # Call the "real" save() method.

    def plan(self, event):
        self.bikes_fulfilled = 0

        if event is None:
            return
        else:
            self.status = "PLANNED"
            self.event = event

    def planable(self):
        return self.status == "ORDERED" or self.status == "DECLINED" or self.status == "PLANNED"

    def invite(self):
        self.status = "INVITED"
        self.date_invite = date.today()

        subject, from_email, to = 'You get your bike with Rückenwind!', 'info@rueckenwind.berlin', self.email
        text_content = 'This is an important message.'
        html_content = '<!DOCTYPE html>' \
                       '<html lang="en">' \
                       '<head>' \
                       '<title>Making Accessible Emails</title>' \
                       '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' \
                       '<meta name="viewport" content="width=device-width, initial-scale=1">' \
                       '<meta http-equiv="X-UA-Compatible" content="IE=edge" />' \
                       '<style type="text/css">' \
                       'body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }' \
                       'table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }' \
                       'img { -ms-interpolation-mode: bicubic; }' \
                       'img { border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }' \
                       'table { border-collapse: collapse !important; }' \
                       'body { height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; }' \
                       '</style>' \
                       '</head>' \
                       '<body style="background-color: aliceblue; margin: 0 !important; padding: 60px 0 60px 0 !important;">' \
                       '<table border="0" cellspacing="0" cellpadding="0" role="presentation" width="100%">' \
                       '<tr>' \
                       '<td bgcolor="aliceblue" style="font-size: 0;">&​nbsp;</td>' \
                       '<td bgcolor="white" width="600" style="border-radius: 4px; color: grey; font-family: sans-serif; font-size: 18px; line-height: 28px; padding: 40px 40px;">' \
                       '<article>' \
                       '<h3 style="color: black; font-size: 32px; font-weight: bold; line-height: 36px; margin: 0 0 30px 0;">Hello ' + self.name + ' ,</h3>' \
                                                                                                                                                   '<img alt="placeholder image" src="http://placehold.it/1200x600" height="75px" width="150px" style="background-color: black; color: white; display: block; font-family: sans-serif; font-size: 18px; font-weight: bold; height: auto; max-width: 100%; text-align: center; width: 100%;">' \
                                                                                                                                                   '<p style="margin: 30px 0 30px 0;">we are happy to invite you to get your bike with Rückenwind. Can you please come on the ' + str(
            self.event.date) + '?</p>' \
                               '<p style="margin: 30px 0 30px 0; text-align: center;">' \
                               '<a href="http://127.0.0.1:8000/fff/order/' + self.hashed_id + '/confirm" target="_blank" style="font-size: 18px; font-family: sans-serif; color: #ffffff; text-decoration: none; border-radius: 8px; -webkit-border-radius: 8px; background-color: #74B843; border-top: 20px solid #74B843; border-bottom: 18px solid #74B843; border-right: 40px solid #74B843; border-left: 40px solid #74B843; display: inline-block;">Yes, I will come.</a>' \
                                                                                              '</p>' \
                                                                                              '<p style="margin: 0 0 30px 0;"> <a href="http://127.0.0.1:8000/fff/order/' + self.hashed_id + '/decline">No, please give me another option.</a></p>' \
                                                                                                                                                                                             '<p style="margin: 0 0 30px 0;"> Your team of Rückenwind</p>' \
                                                                                                                                                                                             '</article>' \
                                                                                                                                                                                             '</td>' \
                                                                                                                                                                                             '<td bgcolor="aliceblue" style="font-size: 0;">&​nbsp;</td>' \
                                                                                                                                                                                             '</tr>' \
                                                                                                                                                                                             '</table>' \
                                                                                                                                                                                             '</body>' \
                                                                                                                                                                                             '</html>'

        send_mail(subject, text_content, from_email, [to], html_message=html_content)

    def confirm(self):
        self.status = "CONFIRMED"
        self.date_answered = date.today()
        self.save()

    def decline(self):
        self.status = "DECLINED"
        self.date_answered = date.today()
        self.save()

    def delete(self):
        self.status = "DELETED"

    def fulfill(self):
        self.bikes_fulfilled = self.bikes_fulfilled + 1
        if int(self.bikes_fulfilled) >= int(self.bikes):
            self.status = "FULFILLED"
        self.save()

    def remove_bike(self):
        self.bikes_fulfilled = self.bikes_fulfilled - 1
        if self.status == "DECLINED" or self.status == "INVITED":
            self.status = "ORDERED"
        self.save()


class Bike(models.Model):
    manufacturer = models.CharField(max_length=30, blank=True, null=True)
    frame_number = models.CharField(max_length=30, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    order = models.ForeignKey(Order, blank=True, null=True, on_delete=models.CASCADE)

    def remove_order(self):
        self.order.remove_bike()
        self.order = None
        self.delete()
