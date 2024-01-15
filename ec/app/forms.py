from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput, TextInput
from . import models

#Create your forms here

class WarehousesForm(forms.ModelForm): #This form will serve two purposes. Create and edit warehouses!
    class Meta:
        model = models.warehouse
        fields = ['address', 'city', 'postal_code', 'country']

        labels = {
            'address': 'Address',
            'city': 'City',
            'postal_code': 'Postal Code',
            'country': 'Country',
        }

        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
            'city': forms.TextInput(attrs={}),
            'postal_code': forms.TextInput(attrs={}),
            'country': forms.TextInput(attrs={}),
        }

        for field in fields:
            widgets[field].attrs['required'] = 'required'

class SupplierForm(forms.ModelForm): #This form will serve two purposes. Create and edit suppliers!
    class Meta:
        model = models.supplier
        fields = ['name', 'phone_number', 'email', 'warehouse']

        labels = {
            'name': 'Supplier Name',
            'phone_number': 'Phone Number',
            'email': 'Email',
            'warehouse': 'Warehouses',
        }

        widgets = {
            'name': forms.TextInput(attrs={}),
            'phone_number': forms.TextInput(attrs={}),
            'email': forms.EmailInput(attrs={}),
            'warehouse': forms.CheckboxSelectMultiple(attrs={}),
        }
        
        for field in fields:
            widgets[field].attrs['required'] = False  # Set required to False for all fields

    def clean_warehouse(self):
        warehouse = self.cleaned_data.get('warehouse')
        if not warehouse:  # Allow the checkbox to be unchecked
            return []
        return warehouse


class ComponentTypeForm(forms.ModelForm): #This form will serve two purposes. Create and edit component types!
    class Meta:
        model = models.component_type
        fields = ['type_name', 'description']

        labels = {
            'type_name': 'Component Type',
            'description': 'Description'
        }

        widgets = {
            'type_name': forms.TextInput(attrs={}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        }
        
        for field in fields:
            widgets[field].attrs['required'] = 'required'

class ComponentForm(forms.ModelForm): #This form will serve two purposes. Create and edit components!
    class Meta:
        model = models.components
        fields = ['name', 'component_type', 'serial_number', 'purchase_date', 'purchase_price', 'supplier', 'image']
        
        labels = {
            'name': 'Name',
            'component_type': 'Type',
            'serial_number': 'Serial Nº',
            'purchase_date': 'Purchase Date',
            'purchase_price': 'Purchase Price',
            'supplier': 'Supplier',
            'image': 'Product Image'
        }

        widgets = {
            'name': forms.TextInput(attrs={}),
            'component_type': forms.Select(attrs={}),
            'serial_number': forms.TextInput(attrs={}),
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'purchase_price': forms.NumberInput(attrs={}),
            'supplier': forms.Select(attrs={}),
            'image': forms.Textarea(attrs={'rows': 2, 'cols': 30, 'placeholder': 'Enter image URL'})
        }

        for field in fields:
            widgets[field].attrs['required'] = False

class EquipmentTypeForm(forms.ModelForm): #This form will serve two purposes. Create and edit equipment types!
    class Meta:
        model = models.equipment_type
        fields = ['type_name', 'description']

        labels = {
            'type_name': 'Equipment Type',
            'description': 'Description'
        }

        widgets = {
            'type_name': forms.TextInput(attrs={}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        }
        
        for field in fields:
            widgets[field].attrs['required'] = 'required'

class CreateEquipmentForm(forms.ModelForm):
    production_description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40})
    )
    production_start = forms.DateTimeField(
        required=True,
        widget=forms.TextInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    production_end = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    labor_type = forms.ModelChoiceField(queryset=models.labor_type.objects.all(), required=True)

    class Meta:
        model = models.equipments
        fields = ['type', 'name', 'serial_number', 'value', 'components']

        labels = {
            'type': 'Equipment Type',
            'name': 'Equipment Name',
            'serial_number': 'Serial Number',
            'value': 'Equipment Value',
        }

        widgets = {
            'name': forms.TextInput(attrs={}),
            'type': forms.Select(attrs={}),
            'serial_number': forms.TextInput(attrs={}),
            'value': forms.NumberInput(attrs={}),
            'components': forms.CheckboxSelectMultiple(attrs={}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        components_queryset = models.components.objects.filter(stock__gt=0)
        self.fields['components'].queryset = components_queryset

    def save(self, commit=True):
        equipment = super().save(commit=False)
        production = models.production(
            description=self.cleaned_data['description'],
            production_start=self.cleaned_data['production_start'],
            production_end=self.cleaned_data['production_end'],
            labor_type=self.cleaned_data['labor_type']
        )
        production.save()
        equipment.save()
        equipment.production = production
        equipment.save()
        return equipment
    
class EditEquipmentForm(forms.ModelForm):
    class Meta:
        model = models.equipments
        fields = ['type', 'name', 'value', 'components']

        labels = {
            'type': 'Equipment Type',
            'name': 'Equipment Name',
            'value': 'Equipment Value',
        }

        widgets = {
            'name': forms.TextInput(attrs={}),
            'type': forms.Select(attrs={}),
            'value': forms.NumberInput(attrs={}),
            'components': forms.CheckboxSelectMultiple(attrs={}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['components'].queryset = models.components.objects.all()

class EditProductionForm(forms.ModelForm):
    production_end = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = models.production
        fields = ['description', 'production_start', 'production_end', 'labor_type']

        labels = {
            'description': 'Description',
            'production_start': 'Production Start',
            'production_end': 'Production End',
            'labor_type': 'Labor Type',
        }

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'production_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'production_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'labor_type': forms.Select(attrs={}),
        }

class ShippingGuidesForm(forms.ModelForm):
    class Meta:
        model = models.shipping_guide
        fields = ['shipping_date', 'delivery_date']

        labels = {
            'shipping_date': 'Shipping Date',
            'delivery_date': 'Delivery Date',
        }

        widgets = {
            'shipping_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'delivery_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    class Meta:
        username = forms.CharField(widget=TextInput()),
        password = forms.CharField(widget=PasswordInput())