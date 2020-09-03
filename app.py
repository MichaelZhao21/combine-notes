from __future__ import print_function
import pickle
import os.path
import json
import re
from collections import OrderedDict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def main():
    print("Authenticating...")
    service = auth()
    print("Authentication Successful!")

    print("Retrieving Data File...")
    data = get_data()
    print("Data File Retrieved Successfully!")

    for d in data:        
        print("Processing Folder ID:", d["folderId"])
        items = get_files(service, d)
        fileGroups, count = parse_files(items, d['formats'])
        print("Loaded", count, "items!")

        print("Combining PDFs...")
        


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
    return build('drive', 'v3', credentials=creds)


def get_data():
    f = open('data.json')
    data = json.load(f)
    f.close()
    return data


def get_files(service, data):
    # Find the given folder
    folderId = data['folderId']

    # Use API to get the list of files in the folder
    # pylint: disable=no-member
    results = service.files().list(
        fields="nextPageToken, files(id, name, parents, mimeType, modifiedTime)",
        spaces='drive',
        q=f"mimeType = 'application/pdf' and '{folderId}' in parents").execute()
    items = results.get('files', [])

    if not items:
        return []
    else:
        return items


def parse_files(items, formats):
    count = 0
    fileGroups = []
    for f in formats:
        mp = re.compile(f["master"])
        p = re.compile(f["regex"])
        if f["subgroup"] == -1:
            d = {}
            masterFile = None
            for i in items:
                m = p.match(i["name"])
                ma = mp.match(i["name"])
                if m:
                    d[m.groups()[0]] = i["id"]
                if ma:
                    masterFile = i["id"]
            if len(d) != 0:
                od = OrderedDict(sorted(d.items()))
                fileGroups.append({
                    'subgroup': False,
                    'files': list(od.values()), 
                    'master': masterFile
                })
                count += len(od)
        else:
            if f["subgroup"] == 0:
                a = 0
                b = 1
            else:
                a = 1
                b = 0
            d = {}
            masterFiles = {}
            for i in items:
                m = p.match(i["name"])
                ma = mp.match(i["name"])
                if m:
                    g = m.groups()
                    if g[a] not in d:
                        d[g[a]] = {}
                    d[g[a]][g[b]] = i["id"]
                    count += 1
                if ma:
                    masterFiles[ma.groups()[0]] = i["id"]
            d2 = {}
            for item in d.items():
                if len(item) != 0:
                    od = OrderedDict(sorted(item[1].items()))
                    d2[item[0]] = list(od.values())
            if len(d2) != 0:
                fileGroups.append({
                    'subgroup': True,
                    'files': d2, 
                    'master': masterFiles
                })
    return (fileGroups, count)


def combine_pdfs(service, fileGroups):
    print(fileGroups)


if __name__ == '__main__':
    main()
