from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'nickname',
            'name',
            # 'billing_profile',
            'address_type',
            'address_line_1',
            'address_line_2',
            'city',
            'province',
            'country',
            'postal_code'
        ]

class AddressCheckoutForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'nickname',
            'name',
            #'billing_profile',
            #'address_type',
            'address_line_1',
            'address_line_2',
            'city',
            'province',
            'country',
            'postal_code'
        ]


