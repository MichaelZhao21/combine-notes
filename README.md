# combine-notes

A simple script to combine google drive files :D I made this mostly for my Rocketbook scans bc it just became an entire Google Drive of PDF scans.

## To Install

```bash
git clone https://github.com/MichaelZhao21/combine-notes.git
cd combine-notes
./install
```

The install script will create the virtual environment folder and install all required packages there. The run script will activate the venv automatically too :)

## Configuration

Go to your Google Cloud API console and create a project, then download an OAuth 2.0 credentials file and move it into a file called 'creds.json'

Replace `cd ~/scripts/combine-notes` in `run` to the absolute path of your combine-notes directory. This will allow you to run this from anywhere.

Create a json file named `data.json` with the following contents:

// TODO: Add complete config info

```json
[
    {
        "folderId": "[The Google Drive ID of the folder you want to combine in]",
        "formats": [
            // This will be a list of file formats you want to combine
            {
                "regex": "[Regular expression with (\\d+) numerical capturing groups",
                "subgroup": "[Number of subgroups to capture (0 means only 1 ordering group)]",
                "master": "[Regular expression for the master files]"
            }
            // ...
        ]
    }
    // ...
]
```

To find the folderID, open the folder in google drive and the url should be `https://drive.google.com/drive/u/0/folders/[folderId]`

### Example formats

```json
{
    "regex": "MATH 3680 - (\\d+).(\\d+).pdf",
    "subgroup": 0,
    "master": "MATH 3680 - Chapter (\\d+).pdf"
}
```

The regex field will find all files named `MATH 3680 - #.#.pdf`. This will include files such as `MATH 3680 - 2.4.pdf` and `MATH 3680 - 4.3.pdf`. For the first file, it will be placed in the `MATH 3680 - Chapter 2.pdf` file while the second will be placed into the `MATH 3680 - Chapter 4.pdf` file.

## Running

To run the program, create the configuration files and run the following command:

```bash
./run
````
