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

- Create a local clone of the repository with the command `git clone --recurse-submodules <repo>`.
- Install dependencies using `Pipenv install`

## To do:

- Create config file that sets up repository. `pyproject.toml`? `setup.py`?
- Create required helper functions.
- Create build script.

Includes forked repositories as submodules. Each is connected to the SLV fork of the original NLNZ repo for development purposes. Need to get installation working to make this less problematic to run the script..