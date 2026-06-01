# services/views/page_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse

from ..models import ServiceCategory

def landing(request):
    categories = ServiceCategory.objects.all()
    return render(
        request,
        'pages/landing.html',
        {'categories': categories}
    )


def pricing(request):
    # return render(request, 'pages/pricing.html')
    # plans = SubscriptionPlan.objects.filter(
    #     active=True
    # )
    plans = (
        SubscriptionPlan.objects
        .filter(active=True)
        .prefetch_related("features")
        .order_by("price")
    )

    context = {
        "plans": plans
    }
    return render(
        request,
        'pages/pricing.html',
      context
    )



def products(request):
    return render(request, 'pages/products.html')

def features(request):
    return render(request, 'pages/features.html')

def docs(request):
    return render(request, 'pages/docs.html')

def contact(request):
    return render(request, 'pages/contact.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def terms(request):
    return render(request, 'pages/terms.html')

# def subscribe(request):
#     return render(request, 'pages/subscribe.html')

def apikey(request):
    return render(request, 'pages/apikey.html')


from django.shortcuts import render
from ..models import SubscriptionPlan,SubscriptionRequest

'''def subscribe(request):
    # plans = SubscriptionPlan.objects.filter(
    #     active=True
    # )
    plan_id = request.GET.get("plan")

    selected_plan = None

    if plan_id:
        selected_plan = get_object_or_404(
            SubscriptionPlan,
            pk=plan_id,
            active=True
        )

    context = {
        "selected_plan": selected_plan
    }

    return render(
        request,
        'pages/subscribe.html',
        context
    )
'''

def dashboard(request):

    return render(
        request,
        'pages/dashboard.html'
    )

@login_required
def subscribe(request):

    plan_id = request.GET.get("plan")

    selected_plan = get_object_or_404(
        SubscriptionPlan,
        pk=plan_id,
        active=True
    )

    if request.method == "POST":

        SubscriptionRequest.objects.create(

            plan=selected_plan,

            full_name=request.POST.get(
                "full_name"
            ),

            email=request.POST.get(
                "email"
            ),

            company=request.POST.get(
                "company"
            )
        )

        return redirect(
            "subscribe_plan",
            selected_plan.id
        )

    return render(
        request,
        "pages/subscribe.html",
        {
            "selected_plan": selected_plan
        }
    )



def health_check(request):
    return JsonResponse({
        "status": "OK",
        "message": "Server is running"
    })

