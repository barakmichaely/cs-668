import os
import re
from shutil import copyfile

def find_healthy_cases():
    bml_folder = "../../data/RawBML/data-384"
    bone_folder = "../../data/BoneMasksFull"

    bml_cases = []
    bone_cases = []
    healthy_cases = []

    # Get all cases
    for f in os.listdir(bml_folder + "/train"):
        # Ignore masks for faster processing
        if "mask" in f:
            continue

        # Extract case number
        regex_match = re.search("^\d+", f)
        case_number = ''
        if (regex_match): 
            case_number = regex_match.group(0).strip()
        else:
            print('Could not extract case number from file name: ' + f)
            continue
        
        bml_cases.append(case_number)

    for f in os.listdir(bml_folder + "/test"):
        # Ignore masks for faster processing
        if "mask" in f:
            continue

        # Extract case number
        regex_match = re.search("^\d+", f)
        case_number = ''
        if (regex_match): 
            case_number = regex_match.group(0).strip()
        else:
            print('Could not extract case number from file name: ' + f)
            continue
        
        bml_cases.append(case_number)

    for f in os.listdir(bml_folder + "/validate"):
        # Ignore masks for faster processing
        if "mask" in f:
            continue

        # Extract case number
        regex_match = re.search("^\d+", f)
        case_number = ''
        if (regex_match): 
            case_number = regex_match.group(0).strip()
        else:
            print('Could not extract case number from file name: ' + f)
            continue
        
        bml_cases.append(case_number)


    # Get cases from bone mask data
    for f in os.listdir(bone_folder):
        # Extract case number
        regex_match = re.search("^\d+", f)
        case_number = ''
        if (regex_match): 
            case_number = regex_match.group(0).strip()
        else:
            print('Could not extract case number from file name: ' + f)
            continue
        
        bone_cases.append(case_number)
        
    # Remove duplicates
    bml_cases = list(dict.fromkeys(bml_cases))
    bone_cases = list(dict.fromkeys(bone_cases))

    print("Done")
    # print(bml_cases)
    print(len(bml_cases))
    print(len(bone_cases))

    for case in bone_cases:
        found = False

        for c in bml_cases:
            if c == case:
                found = True
                break
        
        if found == True:
            healthy_cases.append(case)

    # Done
    print(healthy_cases)
    print(len(healthy_cases))
                

def copy_manual_images():
    manual_folder = '../../data/ManualBML/train'
    mask_folder = '../../data/AllBoneMasks'
    output_folder = '../../data/AllBoneMasks_manual'

    for filename in os.listdir(manual_folder):
        
        if '_mask' in filename:
            continue
        
        mask_name = filename.replace('.bmp', '') + '_mask.bmp'
        mask_path = os.path.join(mask_folder, mask_name)

        try:
            # Copy manual image
            copyfile(os.path.join(manual_folder, filename), os.path.join(output_folder, filename))
            # Copy full bone mask
            copyfile(mask_path, os.path.join(output_folder, mask_name))
            print('Copied: ' + os.path.join(output_folder, filename))
        except:
            print('Err')

    print('Done.')


    
def main():
    # find_healthy_cases()
    copy_manual_images()

if __name__ == '__main__':
    main()