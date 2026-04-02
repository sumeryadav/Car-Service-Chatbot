from django.db import models

# chatbot/models.py
from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.customer.name} - {self.status}"

