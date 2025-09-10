from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanViewSerializer
from .utils import calculate_emi, calculate_credit_score

@api_view(["POST"])
def register(request):
    try:
        data = request.data
        required_fields = ["first_name", "last_name", "age", "phone_number", "monthly_income"]
        for field in required_fields:
            if field not in data:
                return Response({"error": f"'{field}' is required"}, status=status.HTTP_400_BAD_REQUEST)

        monthly_income = float(data["monthly_income"])
        approved_limit = round((36 * monthly_income) / 100000) * 100000

        customer = Customer.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            phone_number=data["phone_number"],
            monthly_income=monthly_income,
            approved_limit=approved_limit,
        )
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def check_eligibility(request):
    try:
        data = request.data
        customer_id = data.get("customer_id")
        if not customer_id:
            return Response({"error": "'customer_id' is required"}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.get(customer_id=customer_id)

        loan_amount = float(data.get("loan_amount", 0))
        interest_rate = float(data.get("interest_rate", 0))
        tenure = int(data.get("tenure", 0))

        score = calculate_credit_score(customer)
        approval = False
        corrected_rate = interest_rate

        if score > 50:
            approval = True
        elif 30 < score <= 50:
            approval = True
            corrected_rate = max(12, interest_rate)
        elif 10 < score <= 30:
            approval = True
            corrected_rate = max(16, interest_rate)

        monthly_installment = calculate_emi(loan_amount, corrected_rate, tenure)
        if monthly_installment > 0.5 * customer.monthly_income:
            approval = False

        return Response({
            "customer_id": customer.customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_rate,
            "tenure": tenure,
            "monthly_installment": monthly_installment
        })

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def create_loan(request):
    try:
        data = request.data
        customer_id = data.get("customer_id")
        if not customer_id:
            return Response({"error": "'customer_id' is required"}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.get(customer_id=customer_id)
        loan_amount = float(data.get("loan_amount", 0))
        interest_rate = float(data.get("interest_rate", 0))
        tenure = int(data.get("tenure", 0))

        score = calculate_credit_score(customer)
        emi = calculate_emi(loan_amount, interest_rate, tenure)

        if score < 10 or emi > 0.5 * customer.monthly_income:
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Loan not approved due to credit score or income ratio",
                "monthly_installment": emi,
            })

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure,
            monthly_installment=emi,
        )

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": True,
            "message": "Loan approved",
            "monthly_installment": emi,
        })

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        return Response(LoanViewSerializer(loan).data)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def view_loans(request, customer_id):
    try:
        loans = Loan.objects.filter(customer_id=customer_id)
        if not loans.exists():
            return Response({"error": "No loans found for this customer"}, status=status.HTTP_404_NOT_FOUND)

        data = [
            {
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "repayments_left": loan.repayments_left,
            }
            for loan in loans
        ]
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
