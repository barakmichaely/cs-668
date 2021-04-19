import os
from shutil import copyfile

def main():
    # Folder structure:   [Phase] > [Case number] > v00 > meta > bone_masks

    input_folder = './phase3'
    output_folder = './data/bone-masks'
    
    # Loop cases
    for case_dir in os.listdir(input_folder):
        if os.path.isdir(os.path.join(input_folder, case_dir)) == False:
            continue

        # Get mask dir
        dir = os.path.join(input_folder, case_dir, 'v00', 'meta', 'bone-masks')
        image_dir = os.path.join(input_folder, case_dir, 'v00', 'meta', 'images')
        
        # Copy all files to output folder
        for filename in os.listdir(dir):
            copyfile(os.path.join(dir, filename), os.path.join(output_folder, filename))
            try:
                image_name = filename.replace('_mask', '')
                copyfile(os.path.join(image_dir, image_name), os.path.join(output_folder, image_name))
            except:
                pass

        

if __name__ == '__main__':
    main()