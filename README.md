# combine-files

A simple script to combine google drive files :D

## To Install

```bash
git clone https://github.com/MichaelZhao21/combine-files.git
cd combine-files
yarn install
```

## Configuration

Create a json file named `data.json` with the following contents:

```json
{
    "folderId": "[The Google Drive ID of the folder you want to combine in]"
}
```

To find the folderID, open the folder in google drive and the url should be `https://drive.google.com/drive/u/0/folders/[folderId]`