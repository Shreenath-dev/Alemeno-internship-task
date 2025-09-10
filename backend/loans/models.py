from django.db import models
from datetime import date

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_income = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.FloatField(default=0)

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)

    @property
    def repayments_left(self):
        months_passed = (date.today().year - self.start_date.year) * 12 + (date.today().month - self.start_date.month)
        return max(0, self.tenure - months_passed)
