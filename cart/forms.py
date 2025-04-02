from django import forms

QUANTITY_CHOICES = ((f"{i}", f"{i} piece{'s' if i > 1 else ''}") for i in range(1, 11))

class AddToCartForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES)