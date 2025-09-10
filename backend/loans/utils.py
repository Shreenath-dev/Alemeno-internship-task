from .models import Loan
from datetime import date

def calculate_emi(principal, rate, tenure):
    r = rate / (12 * 100)
    emi = (principal * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1)
    return round(emi, 2)

def calculate_credit_score(customer):
    loans = Loan.objects.filter(customer=customer)
    score = 50
    if not loans.exists():
        return 60

    for loan in loans:
        score += min(20, loan.emis_paid_on_time)

    score -= len(loans) * 2
    current_year = date.today().year
    recent_loans = loans.filter(start_date__year=current_year).count()
    score += recent_loans * 5

    total_volume = sum([loan.loan_amount for loan in loans])
    score += min(20, total_volume / 1e5)

    current_emis = sum([loan.monthly_installment for loan in loans])
    if current_emis > customer.approved_limit:
        score = 0

    return max(0, min(100, int(score)))
