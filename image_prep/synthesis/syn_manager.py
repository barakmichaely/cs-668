import os, fnmatch, ntpath, re
from shutil import copyfile
import synthesis
import overlay_bml


healthy_folder = ""
bml_folder = ""
bone_mask_folder = ""
# output_folder = "output_data"
output_folder = "output1.1"


####
#### Code Flow for automating the matching of BML slices to healthy slices
####

def auto_synth_full():
    _bml_folder = '../../data/RawBML/data-384/train'
    _bone_folder = '../../data/AllBoneMasks'

    ##### case = '9684122_v00'
    # case = '9184588_v00'
    # case = '9639388_v00'
    case = '9637053_v00'
    # case = '9633944_v00'

    # Tally OG:     30
    # Tally Synth:  +81

    # Get array of slices
    bml_slices = get_case_slices(case, _bml_folder)
    print(bml_slices)
    # print(bml_paths)

    # Get range 
    range = get_bone_range(case, _bone_folder)
    middle = int(range[0] + ((range[1] - range[0]) / 2))

    print(range)
    print(middle)

    # Get array of Gaps
    gaps = get_case_gaps(bml_slices, range, case, _bone_folder)
    print(gaps)


    # Match
    gaps_matched = find_matching_gap_slices(gaps, bml_slices, middle)
    print('\n-- Matched --\n\n')
    # print(gaps_matched)

    # ####
    gap1 = gaps_matched[0]
    print(gap1)
    for gap1 in gaps_matched:
        filename = "auto_" + case + str(gap1[0][0])
        pth_bml = os.path.join(_bml_folder, gap1[1][1])
        pth_bml_mask = pth_bml.replace('.bmp', '_mask.bmp')
        pth_bml_bone = os.path.join(_bone_folder, gap1[1][1].replace('.bmp', '_mask.bmp'))
        
        pth_target = os.path.join(_bone_folder, gap1[0][1])
        pth_target_mask = os.path.join(_bone_folder, gap1[0][1].replace('.bmp', '_mask.bmp'))

        # print('BML Image Path: ' + pth_bml)
        # print('BML Mask Path: ' + pth_bml_mask)
        # print('BML Bone Mask Path: ' + pth_bml_bone)
        # print('Target Image Path: ' + pth_target)
        # print('Target Bone Mask Path: ' + pth_target_mask)
        
        overlay_bml.overlay_bml(pth_bml, pth_bml_mask, pth_bml_bone, pth_target, pth_target_mask, output_folder, filename)
        copyfile(pth_target, os.path.join(output_folder, filename + '_og.bmp'))
        # ####

def auto_synth(case, _bml_folder, _bone_folder):

    # Get array of slices
    bml_slices = get_case_slices(case, _bml_folder)
    # print(bml_slices)

    # Get range 
    range = get_bone_range(case, _bone_folder)
    middle = int(range[0] + ((range[1] - range[0]) / 2))
    # print(range)
    # print(middle)

    # Get array of Gaps
    gaps = get_case_gaps(bml_slices, range, case, _bone_folder)
    print(gaps)


    ## Match
    gaps_matched = find_matching_gap_slices(gaps, bml_slices, middle)
    gaps_to_use = []
    print('\n-- Matched --\n\n')
    # print(gaps_matched)


    ## -- Filter gaps to match amount of original bml slices ---

    # Remove 2 first and 2 last slices, and middle 3 slices from gaps set
    first_range = range[0] + 2
    last_range = range[1] - 2
    print('Len before filter: ' + str(len(gaps_matched)))
    gaps_matched = [item for item in gaps_matched if (item[0][0] > first_range and item[0][0] < last_range) and (item[0][0] < middle - 1 or item[0][0] > middle + 1)]
    print('Len after filter: ' + str(len(gaps_matched)))
    print("Middle: " + str(middle))

    # First, look for exact opposite matches for bml slices
    for g in gaps_matched:
        gap_opposite = g[1]
        gap_num = g[0][0]
        opposite_slice = -1
        if gap_num < middle:
            opposite_slice = middle + (middle - gap_num)
        else:
            opposite_slice = middle - (gap_num - middle)

        for s in bml_slices:
            if opposite_slice == s[0]:
                gaps_to_use.append(g)
                break
    

    # If we still don't have enough items to match original amount of bml slices, get more from gaps list
    if len(bml_slices) > len(gaps_to_use):
        i = 0
        while len(bml_slices) > len(gaps_to_use) and i < len(gaps_matched):
            g = gaps_matched[i]
            i = i + 1
            exists = False
            for _gap in gaps_to_use:
                if _gap[0][0] == g[0][0]:
                    exists = True
                    break
            if exists:
                continue
            else:
                gaps_to_use.append(g)
            

    # print(gaps_matched[0])
    print(len(bml_slices))
    print(len(gaps_to_use))

    # ------------------------------------

    # gaps_to_use = gaps_matched
    # return

    # ####
    for gap1 in gaps_to_use:
        filename = "auto_" + case + str(gap1[0][0])
        pth_bml = os.path.join(_bml_folder, gap1[1][1])
        pth_bml_mask = pth_bml.replace('.bmp', '_mask.bmp')
        pth_bml_bone = os.path.join(_bone_folder, gap1[1][1].replace('.bmp', '_mask.bmp'))
        
        pth_target = os.path.join(_bone_folder, gap1[0][1])
        pth_target_mask = os.path.join(_bone_folder, gap1[0][1].replace('.bmp', '_mask.bmp'))

        # print('BML Image Path: ' + pth_bml)
        # print('BML Mask Path: ' + pth_bml_mask)
        # print('BML Bone Mask Path: ' + pth_bml_bone)
        # print('Target Image Path: ' + pth_target)
        # print('Target Bone Mask Path: ' + pth_target_mask)
        
        overlay_bml.overlay_bml(pth_bml, pth_bml_mask, pth_bml_bone, pth_target, pth_target_mask, output_folder, filename)
        # copyfile(pth_target, os.path.join(output_folder, filename + '_og.bmp'))
        # ####

def synth_all():
    _bml_folder = '../../data/RawBML/new-data-448/train'
    # _bml_folder = '../../data/ManualBML/train'
    _bone_folder = '../../data/AllBoneMasks448'
    
    # count = 0

    cases = []
    for filename in os.listdir(_bml_folder):
        # count = count + 1
        # if count > 5:
        #     break

        if '_mask' in filename:
            continue

        # for testing
        # if not '9000099' in filename:
        #     continue

        case = re.sub('_\d+\..+', '', filename)
        if case in cases:
            continue
            
        cases.append(case)
        

    # print('Case: ' + cases[1])
    # print(len(cases))
    # i = 0
    for case in cases:
        # i = i + 1
        auto_synth(case, _bml_folder, _bone_folder)
        # if i > 3:
        #     break



def get_case_slices(case_number, bone_folder):
    results = find_files('*' + case_number + '*', bone_folder)
    nums = []
    # paths = []
    # print(results)
    for pth in results:
        if '_mask' in pth:
            continue
        filename = ntpath.basename(pth)
        num = filename.replace(case_number, '').replace('.bmp', '')
        num = re.sub('_v\d+_', '', num).replace('_', '')
        
        try:
            num_int = int(num)
            nums.append((num_int, filename))
        except:
            pass
    
    nums.sort()
    return nums

def get_bone_range(case_number, bone_folder):
    nums = get_case_slices(case_number, bone_folder)
    
    if len(nums) == 0:
        return [0, 0]
    
    return [nums[0][0], nums[len(nums) - 1][0]]

def get_case_gaps(slices, case_range, case, bone_folders):
    gaps = []
    for offset in range(case_range[1] - case_range[0] + 1):
        num = case_range[0] + offset
        found = False
        # print(num)
        for pair in slices:
            if pair[0] == num:
                found = True
                break
        
        if found == False:
            search_pattern = case + '*_' + str(num) + '.*'
            bone_files = find_files(search_pattern, bone_folders)
            bone_file = ''
            if len(bone_files) > 0:
                bone_file = bone_files[0]

            gaps.append((num, bone_file))

    return gaps

def find_matching_gap_slices(gaps, bml_slices, middle):
    gaps_matched = []

    for gap in gaps:
        gap_num = gap[0]
        opposite_slice = 0
        if gap_num < middle:
            opposite_slice = middle + (middle - gap_num)
        else:
            opposite_slice = middle - (gap_num - middle)
    
        # Find closest match from bml slices
        closest_distance = 1000
        closest_slice = None
        for s in bml_slices:
            d = abs(s[0] - opposite_slice)
            # print('Comparing: ' + str(s[0]) + ' to ' + str(opposite_slice))
            if (d < closest_distance):
                # print('D: ' + str(d))
                closest_distance = d
                closest_slice = s

        # print('Gap: ' + str(gap_num) + ' -- Opposite: ' + str(opposite_slice))
    # if closest_distance < 1000:
        # print('Closest = ' + str(closest_slice[0]))

        gaps_matched.append((gap, closest_slice))
    
    return gaps_matched


def find_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


##########
##########
###########

# def get_channels():
    


def main():
    # get_channels()
    synth_all()
    return

    bml_case_names = []
    healthy_case_names = []

    # ####
    # filename = "syn_1"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/AllBoneMasks/9184588_v00_33_mask.bmp'
    # # pth_bml = '../../data/RawBml/data-384/train/9122877_v00_13'
    # # pth_bml_bone = '../../data/BoneMasksFull/9122877_v00_13.bmp'
    # pth_healthy = '../../data/AllBoneMasks/9239552_v00_21.bmp'
    # pth_healthy_mask = '../../data/AllBoneMasks/9239552_v00_21_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_2"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9070903_v00_25.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9070903_v00_25_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_3"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9667081_v00_26.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9667081_v00_26_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_4"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9732525_v00_8.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9732525_v00_8_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_5"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9732525_v00_18.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9732525_v00_18_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_6"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9811475_v00_14.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9811475_v00_14_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_7"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9847873_v00_20.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9847873_v00_20_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_8"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9866738_v00_20.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9866738_v00_20_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_9"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9866738_v00_28.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9866738_v00_28_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####
    # ####
    # filename = "syn_10"
    # pth_bml = '../../data/RawBml/data-384/train/9184588_v00_33'
    # pth_bml_bone = '../../data/BoneMasks/9184588_v00_33.bmp'
    # pth_healthy = '../../data/BoneMasksFull/9950688_v00_18.bmp'
    # pth_healthy_mask = '../../data/BoneMasksFull/9950688_v00_18_mask.bmp'
    # pth_mask = pth_bml + '_mask.bmp'
    # pth_bml = pth_bml + '.bmp'
    # ##
    # overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    # ####

    ####
    filename = "syn_11"
    pth_bml = '../../data/RawBml/data-384/train/9395121_v00_18'
    pth_bml_bone = '../../data/AllBoneMasks/9395121_v00_18_mask.bmp'
    pth_healthy = '../../data/BoneMasksFull/9950688_v00_18.bmp'
    pth_healthy_mask = '../../data/BoneMasksFull/9950688_v00_18_mask.bmp'
    pth_mask = pth_bml + '_mask.bmp'
    pth_bml = pth_bml + '.bmp'
    ##
    overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    ####
    ####
    filename = "syn_12"
    pth_bml = '../../data/RawBml/data-384/train/9395121_v00_18'
    pth_bml_bone = '../../data/AllBoneMasks/9395121_v00_18_mask.bmp'
    pth_healthy = '../../data/BoneMasksFull/9070903_v00_25.bmp'
    pth_healthy_mask = '../../data/BoneMasksFull/9070903_v00_25_mask.bmp'
    pth_mask = pth_bml + '_mask.bmp'
    pth_bml = pth_bml + '.bmp'
    ##
    overlay_bml.overlay_bml(pth_bml, pth_mask, pth_bml_bone, pth_healthy, pth_healthy_mask, output_folder, filename)
    ####












    ### -----------------------------------------

    # Extract list of cases from BML folder 
    # Extract list of cases from healthy folder
    
    # Loop BML cases
        # Decide on a healthy folder to use
        # Get all image paths in BML case
        # Loop images
            # Find matching slice
            # --> Create synthetic image + mask
            # Output both to output folder
                # Naming: syn_{bml case}_{healthy case}.bmp, syn_{bml case}_{healthy case}_mask.bmp

if __name__ == '__main__':
    main()

