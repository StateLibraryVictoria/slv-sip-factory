import os
import logging
from sys import exit
from rosetta_sip_factory import sip_builder

# Setup logging
logger = logging.getLogger(__file__)
logging.basicConfig(filename="create_sip.log", level=logging.INFO)
logger.info("Started")

# Get env variables
INPUT_DIR = os.getenv("INPUT_DIR", None)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", None)

# Check input/output directory is specified.
if INPUT_DIR is None:
    print("No input directory specified. Please update .env file to include input directory.")
    exit()
else:
    try:
      INPUT_DIR = os.path.normpath(INPUT_DIR)
    except Exception as e:
      print("Could not normalise input path. Check env. file.")
      print(f"Error: {e}")
      exit()
if OUTPUT_DIR is None:
    print("No output directory specified. Please update .env file to include path to output directory.")
    exit()
else:
    try:
      OUTPUT_DIR = os.path.normpath(OUTPUT_DIR)
    except Exception as e:
      print("Could not normalise output path. Check env. file.")
      print(f"Error: {e}")
      exit()
    
# Check the input directory exists
if not os.path.exists(INPUT_DIR):
    print("Input directory does not exist. Please add path to valid input directory and stage folders for processing.")
    exit()

if not os.path.exists(OUTPUT_DIR):
    print("Making output directory...")
    try:
      os.mkdir(OUTPUT_DIR)
    except Exception as e:
      print(f"Error making output directory: {e}")
      exit()

## Get staged folders.
folders = os.listdir(INPUT_DIR)

# Check input directory is not empty
if len(folders) == 0:
   print("No folders staged in input directory. Stage folders for processing before continuing.")
   exit()

print(f"{len(folders)} folder(s) staged for sip processing: " + ", ".join((folders)) + ".")

for folder in folders:
  logger.info("Processing folder: " + folder)
  # Create input and output paths.
  input_path = os.path.join(INPUT_DIR, folder)
  output_path = os.path.join(OUTPUT_DIR, folder)

  # Check output directory does not exist.
  if os.path.exists(output_path):
     print(f"Warning. Output path for load folder {folder} already exists. Skipping folder.")
     continue

  # Get metadata from folder name
  parts = folder.split("_")
  pi = parts[0] # Preliminary identifier
  title = " ".join(parts[1:]) # Title part
  logging.info("Preliminary identifier: " + pi + ", title: " + title)
  logging.info("Started building SIP.")
  try:
    sip_builder.build_sip(
        ie_dmd_dict=[{'dc:title': folder # title of IE, becomes dc:alternative once split.
                    }],
        pres_master_dir=input_path,
        generalIECharacteristics=[{'IEEntityType': 'None',
                                  'status': 'Original digital content waiting processing'
                                }],
        objectIdentifier=[{'objectIdentifierType': 'preliminary identifier',
                          'objectIdentifierValue': pi}],
        input_dir=input_path,
        digital_original=True,
        sip_title=title,
        output_dir=output_path
    )
    logger.info("Finished building SIP.")
  except Exception as e:
     print(f"Building SIP for folder {folder} failed. Error: {e}")
     logger.info("Building SIP failed.")
     logger.error(f"Error building SIP: {e}")

