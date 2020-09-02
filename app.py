from __future__ import print_function
import pickle
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


def main():
    creds = auth()
    data = get_data()
    combine(creds, data)


def auth():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Load the Drive v3 API
    return creds


def get_data():
    f = open('data.json')
    data = json.load(f)
    f.close()
    return data


def combine(creds, data):
    print(data['folderId'])

    folderId = data['folderId']
    service = build('drive', 'v3', credentials=creds)
    # Find the given folder
    # pylint: disable=no-member
    results = service.files().list(
        pageSize=10, 
        fields="nextPageToken, files(id, name, parents, mimeType, modifiedTime)", 
        spaces='drive', 
        q=f"'{folderId}' in parents").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))


if __name__ == '__main__':
    main()
