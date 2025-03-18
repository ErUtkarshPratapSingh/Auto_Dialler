import os
import django
from django.conf import settings
from celery import shared_task
from .models import Lead
import logging
import requests
from django.db import transaction

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lead_delete.settings")
django.setup()

# API URLs
FETCH_LISTS_API_URL = "https://api-smartflo.tatateleservices.com/v1/broadcast/lists"
FETCH_LEAD_API_URL = "https://api-smartflo.tatateleservices.com/v1/broadcast/leads/{list_id}?number={phone_number}"
DELETE_LEAD_API_URL = "https://api-smartflo.tatateleservices.com/v1/broadcast/lead/{lead_id}"

# API HEADERS
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {settings.SMARTFLO_API_TOKEN}",
}

@shared_task
def process_leads_task(phone_number):
    """Fetches lead list dynamically, finds the lead ID, and deletes the lead."""
    try:
        # 1️⃣ Fetch all lead lists
        list_response = requests.get(FETCH_LISTS_API_URL, headers=HEADERS, timeout=10)
        list_response.raise_for_status()
        lead_lists = list_response.json()

        if not lead_lists:
            return (False, phone_number, "No lead lists found")

        # 2️⃣ Iterate through each list and check if the phone number exists
        for lead_list in lead_lists:
            list_id = lead_list.get("id")
            if not list_id:
                continue

            # 3️⃣ Fetch the lead using the list_id
            fetch_url = FETCH_LEAD_API_URL.format(list_id=list_id, phone_number=phone_number)
            response = requests.get(fetch_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            leads = response.json()

            if not leads:
                continue  # Try the next list

            # 4️⃣ If lead found, delete it
            for lead in leads:
                lead_id = lead.get("lead_id")
                if not lead_id:
                    continue
                
                delete_url = DELETE_LEAD_API_URL.format(lead_id=lead_id)
                delete_response = requests.delete(delete_url, headers=HEADERS, timeout=10)
                delete_response.raise_for_status()
                delete_result = delete_response.json()
                success = delete_result.get("success", False)

                # 5️⃣ Update lead status in the database
                with transaction.atomic():
                    Lead.objects.update_or_create(
                        phone_number=phone_number,
                        defaults={"status": "deleted" if success else "failed"}
                    )

                return (success, phone_number, "Deleted" if success else "Failed")

        return (False, phone_number, "Lead not found in any list")
    
    except requests.RequestException as req_err:
        return (False, phone_number, f"Request error: {req_err}")
    except Exception as e:
        return (False, phone_number, f"Exception: {e}")
