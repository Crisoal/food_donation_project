# services/docusign_service.py

import base64
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from django.http import HttpResponse

# Load environment variables from the .env file
load_dotenv()

def send_docusign_agreement(donor, donation):
    DOCUSIGN_ACCESS_TOKEN = os.getenv("DOCUSIGN_ACCESS_TOKEN")
    DOCUSIGN_ACCOUNT_ID = os.getenv("DOCUSIGN_ACCOUNT_ID")
    DOCUSIGN_BASE_PATH = "https://demo.docusign.net/restapi"

    if not DOCUSIGN_ACCESS_TOKEN or not DOCUSIGN_ACCOUNT_ID:
        print("Error: Missing DocuSign access token or account ID.")
        return

    document_content = f"""
============================
      DONATION AGREEMENT
============================

This Donation Agreement ("Agreement") is entered into on {datetime.now().strftime('%B %d, %Y')} by:

Donor:
Name: {donor.name}
Email: {donor.email}

============================
  TERMS AND CONDITIONS
============================

1. PURPOSE OF AGREEMENT:
   The Donor agrees to donate the specified food items listed below to the Recipient Organization to support its charitable activities. 

2. DONATION DETAILS:
   - Donation ID: {donation.id}
   - Food Items: {', '.join([f"{item['food_type']} (Quantity: {item['quantity']}, Condition: {item['condition']}, Expiration Date: {item['expiration_date']})" for item in donation.food_items])}
   - Pickup Address: {donation.pickup_address}, {donation.city}, {donation.region}, {donation.country}
   - Scheduled Pickup Date: {donation.pickup_date}
   - Scheduled Pickup Time: {donation.pickup_time}

3. DONOR'S RESPONSIBILITIES:
   a. Ensure all donated items meet quality and safety standards.
   b. Confirm availability for pickup at the scheduled time and location.
   c. Provide accurate and complete information about the donated items.

4. RECIPIENT ORGANIZATION'S RESPONSIBILITIES:
   a. Accept the donated items as described in this Agreement.
   b. Ensure the responsible distribution of donated items to beneficiaries.
   c. Provide confirmation of receipt upon delivery.

5. CONDITION OF DONATION:
   a. The Donor affirms that the donated items are free from defects and suitable for consumption.
   b. The Recipient Organization acknowledges that the donation is provided "as is" without warranties of any kind.

6. LIABILITY:
   a. The Donor shall not be held liable for any issues arising after the transfer of donated items.
   b. The Recipient Organization assumes full responsibility for the safe handling and distribution of donated items.

7. CONFIDENTIALITY:
   Both parties agree to keep any shared personal and organizational information confidential and use it solely for the purposes outlined in this Agreement.

8. TERMINATION:
   This Agreement may be terminated by mutual consent of both parties or if either party fails to fulfill its responsibilities as stated.

============================
       SIGNATURES
============================

By signing below, both parties agree to the terms and conditions outlined in this Agreement.

Donor:
Name: {donor.name}
Email: {donor.email}
Signature: 


"""

    encoded_agreement_content = base64.b64encode(document_content.encode('utf-8')).decode('utf-8')

    docusign_api_url = f"{DOCUSIGN_BASE_PATH}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes"
    headers = {
        'Authorization': f'Bearer {DOCUSIGN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

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
                                "pageNumber": "2",
                                "xPosition": "200",
                                "yPosition": "200"
                            }
                        ]
                    }
                }
            ]
        },
        "status": "sent",
    }

    response = requests.post(docusign_api_url, json=payload, headers=headers)

    if response.status_code == 201:
        envelope_id = response.json().get('envelopeId')
        donation.docusign_envelope_id = envelope_id
        donation.agreement_sent = True
        donation.save()

        # Trigger recurring donation setup after agreement is sent
        setup_recurring_donation(donor, donation)
    else:
        print("Failed to send DocuSign agreement:", response.text)


def fetch_signed_agreement(donation):
    DOCUSIGN_ACCESS_TOKEN = os.getenv("DOCUSIGN_ACCESS_TOKEN")
    DOCUSIGN_ACCOUNT_ID = os.getenv("DOCUSIGN_ACCOUNT_ID")
    DOCUSIGN_BASE_PATH = "https://demo.docusign.net/restapi"

    envelope_id = donation.docusign_envelope_id
    if not envelope_id:
        print("Error: Envelope ID not found for the donation.")
        return

    envelope_url = f"{DOCUSIGN_BASE_PATH}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes/{envelope_id}"
    headers = {
        'Authorization': f'Bearer {DOCUSIGN_ACCESS_TOKEN}',
    }

    envelope_response = requests.get(envelope_url, headers=headers)
    if envelope_response.status_code == 200:
        envelope_data = envelope_response.json()
        status = envelope_data.get("status")
        signed_date = envelope_data.get("completedDateTime")

        if status == "completed":
            document_url = f"{DOCUSIGN_BASE_PATH}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes/{envelope_id}/documents/1"
            document_response = requests.get(document_url, headers=headers)
            if document_response.status_code == 200:
                signed_document = base64.b64encode(document_response.content).decode('utf-8')
                donation.signed_document = signed_document
                donation.agreement_signed = True
                donation.agreement_signed_at = signed_date
                donation.save()

                # Setup recurring donation after the agreement is signed
                setup_recurring_donation(donor, donation)
            else:
                print("Failed to fetch signed document:", document_response.text)
        else:
            print("Document not yet signed.")
    else:
        print("Failed to fetch envelope details:", envelope_response.text)




def download_signed_document(donation):
    if not donation.signed_document:
        print("Error: Signed document not available.")
        return None

    # Decode the base64 signed document
    try:
        signed_document = base64.b64decode(donation.signed_document)
    except base64.binascii.Error as e:
        print("Error decoding signed document:", e)
        return None

    # Ensure the 'downloads' directory exists
    download_dir = 'downloads'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Save the decoded content directly as a PDF file
    pdf_file_path = os.path.join(download_dir, f"donation_{donation.id}_signed_agreement.pdf")
    with open(pdf_file_path, 'wb') as pdf_file:
        pdf_file.write(signed_document)

    # Serve the PDF file as a download response
    with open(pdf_file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="donation_{donation.id}_signed_agreement.pdf"'
        return response

