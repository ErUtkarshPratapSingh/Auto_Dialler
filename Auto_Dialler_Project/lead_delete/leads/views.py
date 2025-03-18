from django.shortcuts import render
from django.http import JsonResponse
from .models import Lead
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import process_leads_task
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, "leads/index.html")

@api_view(['POST'])
def webhook_receive(request):
    """Handles incoming webhook data and triggers lead deletion."""
    phone_number = request.data.get("Current", {}).get("Phone")
    
    if not phone_number:
        logger.error("Phone number is missing in the webhook data")
        return JsonResponse({"error" : "Phone Number is Required"}, status = 400) 
    
    # Extract phone number after '-' (if exists)
    if "-" in phone_number:
        phone_number = phone_number.split("-")[-1]
    
    # Create lead entry
    lead, created = Lead.objects.get_or_create(
        phone_number=phone_number,
        defaults={"status" : "pending"}
    )
    
    if created:
        logger.info(f"New lead created: {phone_number}")
    else:
        logger.info(f"Lead already exists: {phone_number}")
    
    try:
        # Trigger Celery task asynchronously
        result = process_leads_task.delay(phone_number)
        logger.info(f"Task queued for phone number {phone_number}, task ID: {result.id}")
    except Exception as e:
        logger.error(f"Failed to queue Celery task for phone number {phone_number}: {e}")
        return JsonResponse({"error" : f"Failed to queue task: {e}"}, status = 500)
    
    return JsonResponse({"message" : "Lead received", "phone_number": phone_number}, status = 201)
