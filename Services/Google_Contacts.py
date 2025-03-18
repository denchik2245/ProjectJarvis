# Просто нанейроненная заглушка.

# import os
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build

# # Если измените эти области, удалите файл token.json.
# SCOPES = ['https://www.googleapis.com/auth/contacts']

# def authenticate_google_contacts():
#     """Authenticate and return the Google Contacts API service."""
#     creds = None
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     return build('people', 'v1', credentials=creds)

# def add_contact(service, name, email):
#     """Add a new contact."""
#     contact = {
#         "names": [{"givenName": name}],
#         "emailAddresses": [{"value": email}]
#     }
#     service.people().createContact(body=contact).execute()
#     print(f'Contact {name} added.')

# def find_contact(service, name):
#     """Find contacts by name."""
#     results = service.people().connections().list(
#         resourceName='people/me',
#         pageSize=10,
#         personFields='names,emailAddresses',
#         requestMask_includeField='person.names,person.emailAddresses'
#     ).execute()
    
#     connections = results.get('connections', [])
#     found_contacts = []
    
#     for person in connections:
#         names = person.get('names', [])
#         if names and names[0].get('displayName') == name:
#             found_contacts.append(person)
    
#     return found_contacts

# def delete_contact(service, resource_name):
#     """Delete a contact by resource name."""
#     service.people().deleteContact(resourceName=resource_name).execute()
#     print(f'Contact {resource_name} deleted.')

# if __name__ == '__main__':
#     service = authenticate_google_contacts()

#     # Пример использования функций
#     add_contact(service, 'John Doe', 'john.doe@example.com')

#     # Поиск контакта
#     found_contacts = find_contact(service, 'John Doe')
#     for contact in found_contacts:
#         print(f'Found contact: {contact}')

#     # Удаление контакта (необходимо указать resourceName)
#     if found_contacts:
#         resource_name = found_contacts[0]['resourceName']
#         delete_contact(service, resource_name)
