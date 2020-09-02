# combine-notes

A simple script to combine google drive files :D

## To Install

```bash
git clone https://github.com/MichaelZhao21/combine-notes.git
cd combine-notes
pip install -r requirements.txt
```

## Configuration

Go to your Google Cloud API console and create a project, then download an OAuth 2.0 credentials file and move it into a file called 'creds.json'

Create a json file named `data.json` with the following contents:

```json
{
    "folderId": "[The Google Drive ID of the folder you want to combine in]"
}
```

To find the folderID, open the folder in google drive and the url should be `https://drive.google.com/drive/u/0/folders/[folderId]`

## Running

To run the program, create the configuration files and run the following command:

```bash

```
