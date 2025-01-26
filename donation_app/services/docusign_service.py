import os
import time
import requests
import base64
import hashlib
import secrets

def generate_code_verifier():
    """Generate a random code verifier for PKCE."""
    return secrets.token_urlsafe(64)

def generate_code_challenge(code_verifier):
    """Generate a code challenge for PKCE using SHA-256."""
    digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode('utf-8')

def is_access_token_expired():
    """Check if the access token is expired."""
    expiry_time = os.getenv("DOCUSIGN_ACCESS_TOKEN_EXPIRY")
    if expiry_time and int(expiry_time) > time.time():
        return False
    return True

def fetch_access_token():
    """Fetches access token, using refresh token if available, or requests reauthorization if necessary."""
    token_url = "https://account-d.docusign.com/oauth/token"
    client_id = os.getenv("DOCUSIGN_CLIENT_ID")
    client_secret = os.getenv("DOCUSIGN_CLIENT_SECRET")

    access_token = os.getenv("DOCUSIGN_ACCESS_TOKEN")
    refresh_token = os.getenv("DOCUSIGN_REFRESH_TOKEN")

    if access_token and not is_access_token_expired():
        return access_token

    if refresh_token:
        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        token_response = requests.post(token_url, data=refresh_data)
        if token_response.status_code == 200:
            tokens = token_response.json()
            os.environ["DOCUSIGN_ACCESS_TOKEN"] = tokens.get("access_token")
            os.environ["DOCUSIGN_REFRESH_TOKEN"] = tokens.get("refresh_token")
            os.environ["DOCUSIGN_ACCESS_TOKEN_EXPIRY"] = str(int(time.time()) + tokens.get("expires_in", 3600))
            return tokens.get("access_token")
        elif token_response.status_code == 400 and "invalid_grant" in token_response.text:
            print("Refresh token expired or invalid. Reauthorization required.")
            os.environ.pop("DOCUSIGN_REFRESH_TOKEN", None)
            os.environ.pop("DOCUSIGN_ACCESS_TOKEN", None)
        else:
            raise Exception(f"Failed to refresh access token: {token_response.text}")

    # Prompt for new authorization if no valid token exists
    print("Authorization required. Please follow the instructions.")
    reauthorize_application()

def reauthorize_application():
    """Guide the user through the reauthorization process."""
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    client_id = os.getenv("DOCUSIGN_CLIENT_ID")
    redirect_uri = os.getenv("DOCUSIGN_REDIRECT_URI", "http://localhost:8000")

    auth_url = "https://account-d.docusign.com/oauth/auth"
    auth_params = {
        "response_type": "code",
        "scope": "signature",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url_with_params = requests.Request('GET', auth_url, params=auth_params).prepare().url
    print("Visit this URL to reauthorize the application and generate a new authorization code:")
    print(auth_url_with_params)
    authorization_code = input("Enter the new authorization code: ")

    # Exchange the authorization code for tokens
    exchange_authorization_code_for_tokens(authorization_code, code_verifier)

def exchange_authorization_code_for_tokens(authorization_code, code_verifier):
    """Exchange the authorization code for access and refresh tokens."""
    token_url = "https://account-d.docusign.com/oauth/token"
    client_id = os.getenv("DOCUSIGN_CLIENT_ID")
    client_secret = os.getenv("DOCUSIGN_CLIENT_SECRET")
    redirect_uri = os.getenv("DOCUSIGN_REDIRECT_URI", "http://localhost:8000")

    token_data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
        "client_secret": client_secret,
    }

    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code == 200:
        tokens = token_response.json()
        os.environ["DOCUSIGN_ACCESS_TOKEN"] = tokens.get("access_token")
        os.environ["DOCUSIGN_REFRESH_TOKEN"] = tokens.get("refresh_token")
        os.environ["DOCUSIGN_ACCESS_TOKEN_EXPIRY"] = str(int(time.time()) + tokens.get("expires_in", 3600))
        print("Access token successfully updated.")
    else:
        raise Exception(f"Failed to exchange authorization code for tokens: {token_response.text}")

def make_docusign_api_request(endpoint, method="GET", data=None, params=None):
    """Make an authenticated API request to the DocuSign API."""
    base_url = "https://demo.docusign.net/restapi/v2.1"
    url = f"{base_url}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {fetch_access_token()}",
        "Content-Type": "application/json",
    }

    response = requests.request(method, url, headers=headers, json=data, params=params)

    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"DocuSign API request failed: {response.status_code} {response.text}")

def send_docusign_agreement(donor, donation):
    """Send a DocuSign agreement using the API for the donation."""
    # Safely extract food item details for display
    food_items_list = [item.get('name', 'Unknown Item') if isinstance(item, dict) else str(item) for item in donation.food_items]

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

    # Fetch access token
    access_token = fetch_access_token()

    # Access the account ID from environment variables
    account_id = os.getenv("DOCUSIGN_ACCOUNT_ID")

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
        # Update donation record (assuming you have a `donation` object with a `save` method)
        donation.agreement_sent = True
        donation.save()
    else:
        print("Failed to send DocuSign agreement:", response.text)


# Example usage
if __name__ == "__main__":
    # Example donor and donation details
    donor = {
        "name": "John Doe",
        "email": "johndoe@example.com",
    }
    donation = {
        "food_items": [
            {"name": "Rice"},
            {"name": "Canned Beans"}
        ],
        "pickup_address": "1234 Donation St.",
        "pickup_date": "2025-02-01",
        "pickup_time": "10:00 AM",
        "agreement_sent": False,
        "save": lambda: print("Donation record updated!")
    }

    send_docusign_agreement(donor, donation)
