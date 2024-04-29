# Overview

A script that builds on National Library of New Zealand's rosetta-sip-factory to create Submission Information Packages for State Library Victoria's digital collections.

## Dependencies

- [lxml](https://lxml.de/)
- [rosetta_sip_factory](https://github.com/StateLibraryVictoria/rosetta_sip_factory)
- [mets_dnx](https://github.com/StateLibraryVictoria/mets_dnx)
- [pymets](https://github.com/StateLibraryVictoria/pymets)
- [pydnx](https://github.com/StateLibraryVictoria/pydnx)
- [pydc](https://github.com/StateLibraryVictoria/pydc)


## Getting started

This project uses Pipenv to manage external libraries (eg. lxml) and git submodule to manage other dependencies which may require or recieve updates over time (eg. pymets, rosetta_sip_factory).

- Basic setup: 
    - Create an empty repository.
    - Add this repository as origin using `git add remote origin <link to repo>`
    - install dependencies using `Pipenv install`.
- To also clone dependencies as submodules (optional): 
    - Run the commands `git submodule init` then `git submodule update`

## Creating SIPS

Basic METS SIPs can be created using `create_sip.py` using the following steps:

- Create an input directory and add path to the .env file. (See `env.example` for an example file.)
- Create an output directory and add path to the .env file.
- Save the .env file.
- Stage folders to be processed in the input directory. Folder titles should have the structure `{preliminary identifier}_{title}_{YYYYMMDD}`
- Launch Pipenv shell using `py -m pipenv shell` or similar.
- Run `py create_sip.py`
- Check the log file `create_sip.log` for details regarding processing.

## To do:

- Create file renaming extension.

## Updating submodules

Not clear how useful this functionality will be, however dependencies were retained as submodules to facilitate development. They may be dropped later. Keeping them separate as submodules allows for updates to be pushed to the original repositories.