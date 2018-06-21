from django.forms import ModelForm, DateInput, TimeInput, Form, TextInput, Textarea, EmailInput, NumberInput
from django import forms
from fff.models import Event, BikeDonation, Collection, LandingContent
from django.utils.translation import gettext


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['date']
        widgets = {
            'date': DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Please select date of event'}),
        }


class LandingContentForm(ModelForm):
    class Meta:
        model = LandingContent
        fields = ['text', 'link']
        widgets = {
            'text': TextInput(
                attrs={'class': 'form-control',
                       'placeholder': gettext('landing_content_form_text_placeholder')}),
            'link': TextInput(
                attrs={'class': 'form-control',
                       'placeholder': gettext('landing_content_form_link_placeholder')}),
        }


class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = ['date', 'capacity']
        widgets = {
            'date': DateInput(
                attrs={'type': 'date', 'class': 'form-control',
                       'placeholder': gettext('collection_form_date_placeholder')}),
            'capacity': NumberInput(
                attrs={'class': 'form-control', 'placeholder': gettext('collection_form_capacity_placeholder')}),
        }


class BikeDonationForm(ModelForm):
    class Meta:
        model = BikeDonation
        fields = ['name', 'email', 'phone', 'address', 'zip', 'latest_pickup', 'bike_count', 'message']
        widgets = {
            'name': TextInput(
                attrs={'class': 'form-control', 'placeholder': gettext('bikedonation_form_name_placeholder')}),
            'email': EmailInput(
                attrs={'class': 'form-control', 'placeholder': gettext('bikedonation_form_email_placeholder')}),
            'phone': TextInput(
                attrs={'class': 'form-control', 'placeholder': gettext('bikedonation_form_phone_placeholder')}),
            'address': TextInput(
                attrs={'class': 'form-control', 'placeholder': gettext('bikedonation_form_address_placeholder')}),
            'zip': TextInput(
                attrs={'class': 'form-control', 'placeholder': gettext('bikedonation_form_zip_placeholder')}),
            'latest_pickup': DateInput(
                attrs={'type': 'date', 'class': 'form-control',
                       'placeholder': gettext('bikedonation_form_latest_pickup_placeholder')}),
            'bike_count': NumberInput(
                attrs={'class': 'form-control', 'placeholder': gettext('bikedonation_form_bike_count_placeholder')}),
            'message': Textarea(
                attrs={'class': 'form-control', 'placeholder': gettext('bikedonation_form_message_placeholder')}),
        }


class ContactForm(Form):
    name = forms.CharField(max_length=100, widget=TextInput(
        attrs={'class': 'form-control', 'placeholder': gettext('contact_form_name_placeholder')}))
    email = forms.EmailField(max_length=100, widget=EmailInput(
        attrs={'class': 'form-control', 'placeholder': gettext('contact_form_email_placeholder')}
    ))
    phone = forms.CharField(max_length=100, widget=TextInput(
        attrs={'class': 'form-control', 'placeholder': gettext('contact_form_phone_placeholder')}
    ))
    message = forms.CharField(max_length=200, widget=Textarea(
        attrs={'class': 'form-control', 'placeholder': gettext('contact_form_message_placeholder')}
    ))

    class Meta:
        widgets = {
        }
