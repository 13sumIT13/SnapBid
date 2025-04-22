from django.forms import ModelForm
from .models import Product, ProductImage, Auction
from django.forms.models import inlineformset_factory
from django import forms
from django.utils import timezone
from django.utils.timezone import is_naive


class ProductForm(ModelForm):
    
    class Meta:
        model = Product
        exclude = ['owner']

ProductImageFormSet = inlineformset_factory(
    Product, ProductImage,
    fields=('image',),
    extra=3,  # Allow up to 3 image uploads
    can_delete=False
)

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['end_time']
        widgets = {
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_end_time(self):
        end_time = self.cleaned_data['end_time']
        if is_naive(end_time):
            return timezone.make_aware(end_time, timezone.get_current_timezone())
        return end_time
    


class AuctionUpdateForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['status', 'end_time']
        widgets = {
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                }
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
