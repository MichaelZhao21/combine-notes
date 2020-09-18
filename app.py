from __future__ import print_function
import pickle
import os
import json
import re
import io
from pdfrw import PdfReader, PdfWriter
from collections import OrderedDict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

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

        fileList, count = parse_files(items, d['formats'], d['folderId'])
        print("Loaded", count, "items!")

        if len(items) > 0:
            print("Combining PDFs...")
            combine_pdfs(service, fileList)
            print("Done!")



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
    # Initiate items and pageToken vars
    items = []
    pageToken = True

    # Use API to get the list of files in the folder
    while pageToken:
        # Check for placeholder pageToken and call the API
        results = call_list_api(
            service, data['folderId'], pageToken if pageToken != True else None)

        # Add the files to the list of items
        items += results.get('files', [])

        # Check to see if there are more files
        if "nextPageToken" in results:
            pageToken = results.get('nextPageToken')
        else:
            pageToken = False

    # Return an empty array if there are no items
    if not items:
        print("There are no items in this folder!")
        return []
    else:
        return items


def call_list_api(service, folderId, pageToken):
    # pylint: disable=no-member
    return service.files().list(
        fields="nextPageToken, files(id, name, parents, mimeType, modifiedTime)",
        spaces='drive',
        pageSize=1000,
        q=f"mimeType = 'application/pdf' and '{folderId}' in parents",
        pageToken=pageToken).execute()


def parse_files(items, formats, folderId):
    # Initialize the counter and main files array
    count = 0
    fileList = []

    # Iterate through the list of format objects
    for f in formats:
        # Create the regex objects
        mp = re.compile(f["master"])
        p = re.compile(f["regex"])

        # Check if there are subgroups
        if f["subgroup"] == -1:
            # If no subgroups
            # Initiate dictionary and masterfile vars
            d = {}
            masterFile = None

            # Iterate through the list of items found
            for i in items:
                # Check if the current item matches the regexes
                m = p.match(i["name"])
                ma = mp.match(i["name"])

                # Add to the list of files or set it as the masterfile
                # if name matches the search terms
                if m:
                    d[int(m.groups()[0])] = i["id"]
                if ma:
                    masterFile = i["id"]

            # If there are matches
            # Put the files into an OrderedDict
            if len(d) != 0:
                od = OrderedDict(sorted(d.items()))

                # Get the sorted list of files
                vals = list(od.values())

                # If the masterfile exists, insert it to the front
                if masterFile:
                    vals.insert(0, masterFile)

                # Append the current file group to the dictionary
                fileList.append({
                    'files': vals,
                    'parent': folderId,
                    'master': f["master"]
                })

                # Increment the count as the number of files
                count += len(vals)

        # If there are subgroups
        else:
            # Check which capturing group is the subgroup
            # and switch the variables if needed
            a, b = 0, 1
            if f["subgroup"] == 1:
                a, b = b, a

            # Initialize the dictionary and masterfile dictionary
            d = {}
            masterFiles = {}

            # Iterate through all the items in the found
            for i in items:
                # Check if the current item matches the regexes
                m = p.match(i["name"])
                ma = mp.match(i["name"])

                # If the file name matches,
                # add it to the correct subgroup
                if m:
                    # Get the capturing groups
                    g = m.groups()

                    # Check to see if the subgroup exists
                    # and add initialize that dictionary if not
                    if int(g[a]) not in d:
                        d[int(g[a])] = {}

                    # Add the item to the subgroup
                    d[int(g[a])][int(g[b])] = i["id"]

                # If the file name matches the masterfile pattern
                # add it to the masterfile dictionary
                if ma:
                    masterFiles[int(ma.groups()[0])] = i["id"]

            # Iterate through the items in the first dictionary
            for item in d.items():

                # If the item has at least one file,
                # put the files into an OrderedDict
                if len(item) != 0:
                    od = OrderedDict(sorted(item[1].items()))

                    # Get the sorted list of files
                    vals = list(od.values())

                    # If the masterfile exists, insert it to the front
                    if item[0] in masterFiles:
                        vals.insert(0, masterFiles[item[0]])

                    # Append the current file group to the dictionary
                    fileList.append({
                        'files': vals,
                        'parent': folderId,
                        'master': f["master"],
                        'subname': item[0]
                    })

                    # Increment the count as the number of files
                    count += len(vals)

    # Return the final fileList and count of files
    return (fileList, count)


def combine_pdfs(service, fileList):
    for group in fileList:
        files = group['files']

        for f in files:
            download_pdf(service, f)

        merge_pdf(service, group, files)
        delete_pdfs(service, group)
        upload_pdf(service, group)


def download_pdf(service, fileId):
    request = service.files().get_media(fileId=fileId)
    fh = io.FileIO(fileId, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        prog = int(status.progress() * 100)
        print(f'{fileId} Download {prog}%.')


def merge_pdf(service, group, files):
    w = PdfWriter()
    for fileId in files:
        r = PdfReader(fileId)
        for page in range(len(r.pages)):
            w.addPage(r.pages[page])
        os.remove(fileId)
    with open('tmp.pdf', 'wb') as p:
        w.write(p)


def delete_pdfs(service, group):
    for f in group["files"]:
        service.files().delete(fileId=f, supportsTeamDrives=True,
                               supportsAllDrives=True).execute()


def upload_pdf(service, group):
    if "subname" in group:
        name = group["master"].replace('(\\d+)', str(group["subname"]))
    else:
        name = group["master"]
    metadata = {'name': name, 'parents': [group['parent']]}
    media = MediaFileUpload('tmp.pdf', mimetype="application/pdf")
    f = service.files().create(body=metadata, media_body=media, fields='id').execute()
    print('Created merged file ID: %s' % f.get('id'))
    os.remove('tmp.pdf')


if __name__ == '__main__':
    main()
