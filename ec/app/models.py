from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class component_type(models.Model):
    component_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50)
    description = models.TextField()
    
    def __str__(self):
        return self.type_name

class warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.address}, {self.postal_code}, {self.city}, {self.country}"

class supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12)
    email = models.EmailField()
    warehouse = models.ManyToManyField(warehouse)
    
    def __str__(self):
        return self.name

class components(models.Model):
    component_id = models.AutoField(primary_key=True)
    component_type = models.ForeignKey(component_type, on_delete=models.CASCADE)
    supplier = models.ForeignKey(supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class equipment_type(models.Model):
    equipment_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.type_name

class labor_type(models.Model):
    labor_type_id = models.AutoField(primary_key=True)
    labor_name = models.CharField(max_length=30, unique=True)
    value = models.PositiveIntegerField()

    def __str__(self):
        return self.labor_name
    
class equipments(models.Model):
    equipment_id = models.AutoField(primary_key=True)
    type = models.ForeignKey(equipment_type, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=100, unique=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    components = models.ManyToManyField(components)

    def __str__(self):
        return self.name

class production(models.Model): 
    production_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100)
    production_start = models.DateTimeField(default=timezone.now)
    production_end = models.DateTimeField(null=True)
    labor_type = models.ForeignKey(labor_type, on_delete=models.CASCADE)
    equipment = models.ForeignKey(equipments, on_delete=models.CASCADE)
    status = models.BooleanField(null=True)

    def __str__(self):
        return self.description

class shipping_guide(models.Model):
    guide_id = models.AutoField(primary_key=True)
    shipping_date = models.DateTimeField(null=True)
    delivery_date = models.DateTimeField(null=True)

class orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateField(auto_now_add=True)
    equipment = models.ForeignKey(equipments, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    shipping_guide = models.OneToOneField(shipping_guide, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  