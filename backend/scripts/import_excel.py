import os
import sys
sys.path.append("/app")  # ensures Django project is in path

import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "credit_system.settings")
django.setup()

from loans.models import Customer, Loan


customer_file = "data/customer_data.xlsx"
loan_file = "data/loan_data.xlsx"


customers_df = pd.read_excel(customer_file)
for _, row in customers_df.iterrows():
    Customer.objects.update_or_create(
        customer_id=row["Customer ID"],
        defaults={
            "first_name": row["First Name"],
            "last_name": row["Last Name"],
            "age": row["Age"],
            "phone_number": str(row["Phone Number"]),
            "monthly_income": row["Monthly Salary"],
            "approved_limit": row["Approved Limit"],
        }
    )

# ---------- Import Loans ----------
loans_df = pd.read_excel(loan_file)
for _, row in loans_df.iterrows():
    try:
        customer = Customer.objects.get(customer_id=row["Customer ID"])
    except Customer.DoesNotExist:
        print(f"Customer ID {row['Customer ID']} not found, skipping loan {row['Loan ID']}")
        continue

    Loan.objects.update_or_create(
    loan_id=row["Loan ID"],
    defaults={
        "customer": customer,
        "loan_amount": row["Loan Amount"],
        "tenure": row["Tenure"],
        "interest_rate": row["Interest Rate"],
        "monthly_installment": row["Monthly payment"],
        "emis_paid_on_time": row.get("EMIs paid on Time", 0),
        "start_date": pd.to_datetime(row.get("Date of Approval"), errors="coerce").date() if row.get("Date of Approval") else date.today(),
        "end_date": pd.to_datetime(row.get("End Date"), errors="coerce").date() if row.get("End Date") else None,
    }
)



print("Data import complete!")
