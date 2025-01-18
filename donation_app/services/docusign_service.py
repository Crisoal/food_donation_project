# donation_app/services/docusign_service.py

import base64
import os
import requests

def send_docusign_agreement(donor, donation):
    # Safely extract food item details for display
    food_items_list = []
    for item in donation.food_items:
        # Assuming each item is a dictionary with a 'name' key
        if isinstance(item, dict):
            food_items_list.append(item.get('name', 'Unknown Item'))
        else:
            food_items_list.append(str(item))  # Handle unexpected cases

    # Generate agreement content dynamically
    agreement_content = f"""
    Dear {donor.name},

    Thank you for your generous donation. Below are the details of the donation agreement:
    
    Food Items: {", ".join(food_items_list)}
    Donor Address: {getattr(donor, 'pickup_address', 'N/A')}
    Pickup Date and Time: {getattr(donation, 'pickup_date', 'N/A')} at {getattr(donation, 'pickup_time', 'N/A')}
    
    By signing this agreement, you confirm that the food items listed above will be donated to Food Donation Hub, and the organization will handle the distribution to non-profits in need.

    Please review and sign the agreement to complete the process.
    """

    # Base64 encode the agreement content
    encoded_agreement_content = base64.b64encode(agreement_content.encode('utf-8')).decode('utf-8')

    # Access the account ID and access token from environment variables
    account_id = os.getenv("DOCUSIGN_ACCOUNT_ID")
    access_token = os.getenv("DOCUSIGN_ACCESS_TOKEN")

    # DocuSign API URL
    docusign_api_url = f"https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    payload = {
        "emailSubject": "Food Donation Agreement",
        "documents": [
            {
                "documentBase64": encoded_agreement_content,
                "name": "Donation Agreement",
                "fileExtension": "txt",
                "documentId": "1",
            }
        ],
        "recipients": {
            "signers": [
                {
                    "email": donor.email,
                    "name": donor.name,
                    "recipientId": "1",
                    "routingOrder": "1",
                }
            ]
        },
        "status": "sent",
    }
    response = requests.post(docusign_api_url, json=payload, headers=headers)
    if response.status_code == 201:
        # Update donation record
        donation.agreement_sent = True
        donation.save()
    else:
        print("Failed to send DocuSign agreement:", response.text)
