import os
import shutil
import logging
import urllib
import urllib.parse
from lxml import etree as ET

## setup logging
logger = logging.getLogger()

def move_rename_files(root_directory, mets_filename="mets.xml"):
    """A function that takes an existing SIP, checks for non-ascii filenames, creates a renamed
    copy of those files in a renamed/ directory in streams and updates the href tag in the FLocat 
    area of the METS manifest.
    
    Args: 
        root_directory (path/str) : The location of the SIP. 
        mets_filename (str) : Defaults to "mets.xml", but can be used to specify filename if one has been used."""
    # Parse the mets from the file location.
    mets_file = os.path.join(root_directory, "content", mets_filename)
    mets = ET.parse(mets_file)

    # Set the directory for renamed files.
    rename_dir = os.path.join(root_directory,"content", "streams", 'renamed')
    if os.path.exists(rename_dir):
         rename_dir = os.path.join(rename_dir, "slv_rosetta_sip_preparation")

    # Iterate through files and rename them if they are not ASCII. Update the href so that the file can be resolved.
    for fl in mets.findall(".//{http://www.loc.gov/METS/}FLocat"):
            fl_id = fl.getparent().attrib['ID']
            root, ext = os.path.splitext(fl.attrib["{http://www.w3.org/1999/xlink}href"])
            if not root.isascii():
                logger.info(f"File: {root + ext} with file id {fl_id} contains non-ascii characters. File will be renamed.")
                fl.attrib["{http://www.w3.org/1999/xlink}href"] = os.path.join("renamed",fl_id + ext)
                logger.debug(f"METS updated for file {root+ext}")
                if not os.path.exists(rename_dir):
                     os.mkdir(rename_dir)
                logger.info("Copying file to new location...")
                try:
                    shutil.copy2(os.path.join(root_directory, "content", "streams", root+ext), os.path.join(rename_dir, fl_id+ext))
                    logger.info("File copied.")
                except Exception as e:
                    print(f"Error copying file: {root+ext}. Error message: {e}")
                    logger.error(f"Error copying file: {root+ext}. Error message: {e}")
            else: # Percent encodes all other refs.
                fl.attrib["{http://www.w3.org/1999/xlink}href"] = urllib.parse.quote(fl.attrib["{http://www.w3.org/1999/xlink}href"], encoding='utf-8')
    with open(mets_file, 'wb') as mf:
         mf.write(ET.tostring(mets, xml_declaration=True, encoding='utf-8'))
    return None
