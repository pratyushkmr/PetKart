from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


Payment_Choices=(
        ('S', 'Stripe'),('P','Paypal'))

class Checkoutform(forms.Form):
    street_address= forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Address Line 1'}))
    apartment_address=forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder':'Address Line 2'}))
    country=CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
            'class':'custom-select d-blockw-100'}))
    zip=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    same_shipping_address=forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    save_info=forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    paymen_option=forms.ChoiceField(
            widget=forms.RadioSelect, choices=Payment_Choices)
    
    