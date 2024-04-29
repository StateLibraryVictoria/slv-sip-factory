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

## To do:

- Create required helper functions.
- Create build script.

## Updating submodules

Not clear how useful this functionality will be, however dependencies were retained as submodules to facilitate development. They may be dropped later. Keeping them separate as submodules allows for updates to be pushed to the original repositories.