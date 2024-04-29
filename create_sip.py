import os
from rosetta_sip_factory.rosetta_sip_factory import sip_builder

def cleanup_folder(paths):
    for local_path in paths:
        if os.path.exists(local_path):
            count = 0
            for root, dir, files in os.walk(local_path):
                #remove files
                file_list = [os.path.join(root, file) for file in files]
                for item in file_list:
                    try:
                        os.remove(item)
                        count += 1
                    except Exception as e:
                        print(f"Error removing files: {e}")
        print(f"Removed {count} files from {local_path}")

# cleanup
cleanup_folder(["output_dir"])

# set the base directory
folder = "RA-2022-87_Lew_Hillier_Papers_test_unicode_folder_utf_8"
base_dir = os.path.join(folder)
output_dir = os.path.join("output_dir")

parts = folder.split("_")
pi = parts[0]
title = " ".join(parts[1:])

sip_builder.build_sip(
    ie_dmd_dict=[{'dc:title': folder # title of IE, becomes dc:alternative once split.
                }],
    pres_master_dir=os.path.join(base_dir),
    generalIECharacteristics=[{'IEEntityType': 'None',
                               'status': 'Original digital content waiting processing'
                             }],
    objectIdentifier=[{'objectIdentifierType': 'preliminary identifier',
                       'objectIdentifierValue': pi}],
    input_dir=base_dir,
    digital_original=True,
    sip_title=title,
    output_dir=output_dir
)

