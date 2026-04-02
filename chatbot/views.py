
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Service, Customer, Appointment
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def home(request):
    return render(request, "chatbot/home.html")

def chat_page(request):
    return render(request, "chatbot/chat.html")

@csrf_exempt
def chatbot_view(request):
    """
    Renders the main chatbot interface page.
    This view is called when you visit /chat/ in the browser.
    """
    request.session.flush()
    return render(request, "chatbot/chat.html")

# chatbot/views.py

@csrf_exempt
def chatbot_api(request):
    step = request.session.get('step', 'greet')
    response = ""
    options = []

    if step == 'greet':
        response = "Hello! Welcome to Car Service Bot. What services would you like? (You can choose multiple)"
        options = [s.name for s in Service.objects.all()] + ["done"]
        request.session['step'] = 'service'
        request.session['selected_services'] = []

    elif step == 'service':
        selected = request.POST.get("message")
        if selected and selected.lower() != "done":
            try:
                service = Service.objects.get(name=selected)
                request.session['selected_services'].append(service.id)
                response = f"Added {service.name}. You can add more or type 'done' when finished."
                options = [s.name for s in Service.objects.all()] + ["done"]
            except Service.DoesNotExist:
                response = "Sorry, I didn’t recognize that service. Please choose again."
                options = [s.name for s in Service.objects.all()] + ["done"]
        elif selected and selected.lower() == "done":
            request.session['step'] = 'location'
            maps_url = "https://www.google.com/maps"
            response = (
                f"Great! Please provide your location 👉 "
                f"<a href='{maps_url}' target='_blank' class='text-blue-600 underline'>Open Google Maps</a>"
            )

    elif step == 'location':
        location = request.POST.get("message")
        if location:
            request.session['location'] = location
            request.session['step'] = 'datetime'
            maps_url = f"https://www.google.com/maps/search/?api=1&query={location.replace(' ', '+')}"

            # Fixed pricing by location
            location_lower = location.lower()
            if "delhi" in location_lower:
                total_price = 5000
            elif "gurugram" in location_lower:
                total_price = 7000
            elif "faridabad" in location_lower:
                total_price = 7000
            elif "greater noida" in location_lower:
                total_price = 8500
            elif "noida" in location_lower:
                total_price = 8000
            elif "ghaziabad" in location_lower:
                total_price = 4000
            else:
                total_price = sum([s.price for s in Service.objects.filter(id__in=request.session['selected_services'])])

            request.session['calculated_price'] = total_price

            response = (
                f"✅ Location automatically set: {location} "
                f"<a href='{maps_url}' target='_blank' class='text-blue-600 underline'>📍 View on Google Maps</a><br>"
                f"Fixed price for {location}: ₹{total_price}.<br>"
                "Now, please provide your preferred date and time for the service."
            )
        else:
            response = "Please enter a valid location."

    elif step == 'datetime':
        datetime_input = request.POST.get("message")
        if datetime_input:
            request.session['datetime'] = datetime_input
            request.session['step'] = 'confirm'
            services = Service.objects.filter(id__in=request.session['selected_services'])
            service_names = ", ".join([s.name for s in services])
            total_price = request.session.get('calculated_price', sum([s.price for s in services]))
            response = (
                f"Your services: {service_names} at {request.session['location']} "
                f"on {datetime_input}. Total price: ₹{total_price}. "
                "Confirm appointment? (yes/no)"
            )
        else:
            response = "Please enter a valid date and time."

    elif step == 'confirm':
        confirm = request.POST.get("message")
        if confirm and confirm.lower() == "yes":
            customer = Customer.objects.create(
                name="Guest User", email="guest@example.com", phone="0000000000",
                location=request.session['location']
            )
            appointment = Appointment.objects.create(
                customer=customer,
                datetime=request.session.get('datetime', None)  # optional field if your model supports it
            )
            appointment.services.set(request.session['selected_services'])
            appointment.status = "Confirmed"
            appointment.save()
            response = "✅ Appointment confirmed! Thank you."
            request.session['step'] = 'greet'
            request.session['selected_services'] = []
        else:
            response = "❌ Appointment cancelled."
            request.session['step'] = 'greet'
            request.session['selected_services'] = []

    return JsonResponse({"response": response, "options": options})