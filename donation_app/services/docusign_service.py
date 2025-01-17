# donation_app/services/docusign_service.py

import requests

def send_docusign_agreement(donor, donation):
    # Generate agreement content dynamically
    agreement_content = f"""
    Dear {donor.name},

    Thank you for your generous donation. Below are the details of the donation agreement:
    
    Food Items: {", ".join(donation.food_items)}
    Donor Address: {donor.address}
    Pickup Date and Time: {donation.pickup_date} at {donation.pickup_time}
    
    By signing this agreement, you confirm that the food items listed above will be donated to Food Donation Hub, and the organization will handle the distribution to non-profits in need.

    Please review and sign the agreement to complete the process.
    """

    # DocuSign API URL and access token placeholders
    docusign_api_url = "https://demo.docusign.net/restapi/v2.1/accounts/{account_id}/envelopes"
    headers = {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
        'Content-Type': 'application/json',
    }
    payload = {
        "emailSubject": "Food Donation Agreement",
        "documents": [
            {
                "documentBase64": agreement_content.encode('utf-8').decode('ascii'),
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
