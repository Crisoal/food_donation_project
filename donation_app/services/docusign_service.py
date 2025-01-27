import base64
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

def send_docusign_agreement(donor, donation):
    DOCUSIGN_ACCESS_TOKEN = os.getenv("DOCUSIGN_ACCESS_TOKEN")
    DOCUSIGN_ACCOUNT_ID = os.getenv("DOCUSIGN_ACCOUNT_ID")
    DOCUSIGN_BASE_PATH = "https://demo.docusign.net/restapi"

    # Check if DocuSign credentials are available
    if not DOCUSIGN_ACCESS_TOKEN or not DOCUSIGN_ACCOUNT_ID:
        print("Error: Missing DocuSign access token or account ID.")
        return

    # Prepare document content
    document_content = f"""
    Donation Agreement:
    Donor: {donor.name}
    Email: {donor.email}
    Donation ID: {donation.id}
    Food Items: {donation.food_items}
    Pickup Address: {donation.pickup_address}, {donation.city}, {donation.region}, {donation.country}
    Pickup Date: {donation.pickup_date}
    Pickup Time: {donation.pickup_time}
    """

    # Base64 encode the document content
    encoded_agreement_content = base64.b64encode(document_content.encode('utf-8')).decode('utf-8')

    docusign_api_url = f"{DOCUSIGN_BASE_PATH}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes"
    
    headers = {
        'Authorization': f'Bearer {DOCUSIGN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

    # Prepare payload for sending the document
    payload = {
        "emailSubject": "Please sign the donation agreement",
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
                    "tabs": {
                        "signHereTabs": [
                            {
                                "documentId": "1",
                                "pageNumber": "1",
                                "xPosition": "200",
                                "yPosition": "300"
                            }
                        ]
                    }
                }
            ]
        },
        "status": "sent",
    }

    # Send request to DocuSign API
    response = requests.post(docusign_api_url, json=payload, headers=headers)

    if response.status_code == 201:
        donation.agreement_sent = True
        donation.save()
        print("DocuSign agreement sent successfully.")
    else:
        print("Failed to send DocuSign agreement:", response.text)

def fetch_signed_agreement(donation):
    DOCUSIGN_ACCESS_TOKEN = os.getenv("DOCUSIGN_ACCESS_TOKEN")
    DOCUSIGN_ACCOUNT_ID = os.getenv("DOCUSIGN_ACCOUNT_ID")
    DOCUSIGN_BASE_PATH = "https://demo.docusign.net/restapi"

    # Get the envelope ID from the donation object (should be stored when sending agreement)
    envelope_id = donation.docusign_envelope_id  # Assuming you store the envelope ID in the model

    # DocuSign API URL to fetch the document
    docusign_api_url = f"{DOCUSIGN_BASE_PATH}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes/{envelope_id}/documents/1"

    headers = {
        'Authorization': f'Bearer {DOCUSIGN_ACCESS_TOKEN}',
    }

    # Fetch the signed document
    response = requests.get(docusign_api_url, headers=headers)

    if response.status_code == 200:
        # Save the signed document in the donation record
        signed_document = base64.b64encode(response.content).decode('utf-8')
        donation.signed_document = signed_document
        donation.agreement_signed = True
        donation.agreement_signed_at = datetime.now()  # Store the timestamp of signing
        donation.save()
        print("Signed agreement fetched successfully.")
    else:
        print("Failed to fetch signed agreement:", response.text)
