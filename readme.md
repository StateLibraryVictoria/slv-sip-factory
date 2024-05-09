# Overview

A script that builds on National Library of New Zealand's [rosetta-sip-factory](https://github.com/NLNZDigitalPreservation/rosetta_sip_factory) to create Submission Information Packages for State Library Victoria's digital collections. See the diagrams section at the end of this guide for an overview of program logic.

## Dependencies

- [lxml](https://lxml.de/)
- [rosetta_sip_factory](https://github.com/StateLibraryVictoria/rosetta_sip_factory)
- [mets_dnx](https://github.com/StateLibraryVictoria/mets_dnx)
- [pymets](https://github.com/StateLibraryVictoria/pymets)
- [pydnx](https://github.com/StateLibraryVictoria/pydnx)
- [pydc](https://github.com/StateLibraryVictoria/pydc)


## Getting started

This project uses Pipenv to manage external libraries including dependencies that exist as repositories on Github only. 

- Basic setup: 
    - Create an empty repository.
    - Add this repository as origin using `git add remote origin <link to repo>`
    - install dependencies using `Pipenv install`.

## Creating SIPS

Basic METS SIPs can be created using `create_sip.py` using the following steps:

- Create an input directory and add path to the `.env` file. (See `env.example` for an example file.)
- Create an output directory and add path to the `.env` file.
- Save the `.env` file.
- Stage folders to be processed in the input directory. Folder titles should have the structure `{preliminary identifier}_{title}_{YYYYMMDD}`.
- Launch Pipenv shell using `py -m pipenv shell` or similar.
- Run `py create_sip.py`.
- Check the log file `create_sip.log` for details regarding processing.

Current configuration assumes:
- The folder titles have a preliminary identifier as the first part. The preliminary identifier does not contain underscores.
- The preliminary identifier is recorded on an ArchivesSpace record for the material.

### File renaming

Files are renamed during post-processing of the METS manifest to ensure the files can be located by Rosetta. The original filenames and folder paths are captured as metadata in the METS manifest, which is reapplied to the file upon download.

### dc.xml

The `dc.xml` file contains SIP metadata that can be searched in Rosetta. This file is created after the renaming process, using `<rosetta:externalSystem>` and `<rosetta:externalId>` tags to record the preliminary identifier and system where the material is registered. This is defined in Rosetta documentation for [Depositing Content Automatically](https://knowledge.exlibrisgroup.com/Rosetta/Product_Documentation/Rosetta_Producer%27s_Guide/004_Depositing_Content/004_Automated_Deposit#Depositing_Content_Automatically).

## Diagrams

### Activity diagram

![activity diagram](docs/sip_file_renamer-Activity_diagram.drawio.svg)

### Program logic

![program logic diagram](docs/sip_file_renamer-Logic_diagram.drawio.svg)
