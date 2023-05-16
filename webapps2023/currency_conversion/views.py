from rest_framework.decorators import api_view
from rest_framework.response import Response

# Hardcoded Exchange Rates (21-04-2023)
EXCHANGE_RATES = {
    # 2023 April Rates
    'GBP': 1.0,
    'USD': 1.24,
    'EUR': 1.13,
}

# REST api Implementation
@api_view(['GET'])
def convert_currency(request):
    source_currency = request.GET.get('source')
    target_currency = request.GET.get('target')
    amount = float(request.GET.get('amount', 0))

    if source_currency not in EXCHANGE_RATES or target_currency not in EXCHANGE_RATES:
        return Response({"error": "Invalid source or target currency."}, status=400)

    converted_amount = amount * EXCHANGE_RATES[target_currency] / EXCHANGE_RATES[source_currency]

    return Response({"converted_amount": round(converted_amount, 2)})