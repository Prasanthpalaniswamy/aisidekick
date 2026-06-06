# chat_completion_api()
# usage_api()
# apikey_validation()
# webhook_handlers()
from django.utils import timezone

from django.http import JsonResponse
from services.models import APIKey,Subscription


def validate_api_key(request):

    api_key  = request.headers.get(
        "X-API-Key"
    )

    if not api_key:

        return JsonResponse(
            {"valid": False,
                "message": "API key missing"},
            status=401
        )
    key = APIKey.objects.filter(
        key=api_key,
        is_active=True
    ).select_related(
        "user"
    ).first()

    if not key:

        return JsonResponse(
            {
                "valid": False,
                "message": "Invalid API key/ API key is missing or inactive"
            },
            status=401
        )
    
    active_subscriptions = Subscription.objects.filter(user=key.user,
    status="ACTIVE", expires_at__gt=timezone.now()).select_related("plan")
    if not active_subscriptions.exists():

        return JsonResponse(
            {
                "valid": False,
                "message": "No active subscriptions"
            },
            status=403
        )

    plans = [
        sub.plan.name
        for sub in active_subscriptions
    ]
    return JsonResponse(
    {
        "valid": True,
        "user_id": key.user.id,
        "username": key.user.username,
        "plans": plans,
        "products": [
        sub.plan.product_code
        for sub in active_subscriptions],
    "expires_at": max(
        sub.expires_at
        for sub in active_subscriptions
    ).isoformat()
    }
)

    # exists = APIKey.objects.filter(
    #     key=key,
    #     is_active=True
    # ).exists()

    # return JsonResponse(
    #     {
    #         "valid": exists
    #     }
    # )