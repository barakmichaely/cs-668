import cv2
import mask_helper
import math
import line_helper
import synthesis
import os
import random
from PIL import Image
import numpy as np

random.seed(1) # This ensures we get the exact same 'random' pattern every time we generate images

def main_1():
    ### 1. Load images
    # Load source images
    src_path = '../../data/RawBml/data-384/train/9184588_v00_33.bmp'
    src_img = cv2.imread(src_path)

    src_bml_path = '../../data/RawBml/data-384/train/9184588_v00_33_mask.bmp'
    src_bml = cv2.imread(src_bml_path, 0)

    src_bone = cv2.imread('../../data/BoneMasks/9184588_v00_33.bmp', 0)
    
    # Load target images
    target_path = '../../data/RawBml/data-lite-384/train/9014883_v00_25.bmp'
    target_img = cv2.imread(target_path)

    target_bone_path = '../../data/BoneMasks/9014883_v00_25.bmp'
    target_bone = cv2.imread(target_bone_path, 0)

    img_size = len(src_bone)

    #### 2. Calculate new bml location
    angle, bml_distance, bone_distance = mask_helper.get_bml_distance(src_bone, src_bml)
    # source_bone_center = mask_helper.get_mask_center(src_bone)
    src_bml_center = mask_helper.get_mask_center(src_bml)
    target_bone_center = mask_helper.get_mask_center(target_bone)
    bone_center = target_bone_center
    
    ## Create line to intersect with bone edges
    unit_vector = (math.cos(angle), math.sin(angle))
    vector = (unit_vector[0] * img_size, unit_vector[1] * img_size)
    projected_point = (int(bone_center[0] + vector[0]), int(bone_center[1] + vector[1]))
    
    ## Get bone edges + intersection point
    bone_edges = mask_helper.get_mask_edges(target_bone)
    edge_point = mask_helper.get_closest_edge_to_line(bone_edges, bone_center, projected_point, img_size)

    ## Find where bml center point should be
    bml_point = (
        int(edge_point[0] - (unit_vector[0] * bml_distance)),
        int(edge_point[1] - (unit_vector[1] * bml_distance)),
    )
    bml_diff_x = bml_point[0] - src_bml_center[0]
    bml_diff_y = bml_point[1] - src_bml_center[1]

    ########

    #### 3. Place bml on target image
    img = synthesis.extract_mask_region_from_path(
        src_path, src_bml_path, 
        target_path, target_bone_path,
        bml_diff_x, bml_diff_y)

    cv2.imwrite('./output/overlay-test-plain.bmp', img)

    ## Draw info to image (for easier testing)
    # img = cv2.cvtColor(target_img, cv2.COLOR_GRAY2BGR)
    # img = target_img
    img = cv2.circle(img, 
        (int(bone_center[0]), int(bone_center[1])),
        5, (0,0,255), 4
        )
    img = mask_helper.draw_mask_contours(target_bone, img)
    # img = cv2.line(img, p1, p2, (0,0,0), 2)
    img = cv2.line(img, bone_center, projected_point, (255,0,0), 1)
    img = cv2.circle(img, edge_point, 2, (0,0,255), 2)
    img = cv2.circle(img, bml_point, 2, (255,0,0), 2)
    # img = cv2.circle(img, src_bml_center, 1, (255,0,0), 2)

    cv2.imwrite('./output/overlay-test.bmp', img)
    

def overlay_bml(bml_path, bml_mask_path, bml_bone_mask_path, target_path, target_bone_mask_path, output_folder, filename):
    #### 1. Load images
    # bml_path = '../../data/RawBml/data-384/train/9184588_v00_33.bmp'
    # bml_mask_path = '../../data/RawBml/data-384/train/9184588_v00_33_mask.bmp'
    # bml_bone_mask_path = '../../data/BoneMasks/9184588_v00_33.bmp'
    # target_path = '../../data/RawBml/data-lite-384/train/9014883_v00_25.bmp'
    # target_bone_mask_path = '../../data/BoneMasks/9014883_v00_25.bmp'

    # src_img = cv2.imread(bml_path)
    src_bml = cv2.imread(bml_mask_path, 0)
    src_bone = cv2.imread(bml_bone_mask_path, 0)
    # target_img = cv2.imread(target_path)
    target_bone = cv2.imread(target_bone_mask_path, 0)
    #
    img_size = len(src_bone)

    #### 2. Calculate new bml location
    angle, bml_distance, bone_distance, bml_radius = mask_helper.get_bml_distance(src_bone, src_bml)
    
    # Randomly increase distance from edge
    # random_distance = random.uniform(0.8, 1.5)
    # bml_distance = bml_distance * random_distance 
    bml_distance = bml_radius - 5
    # bml_distance = bml_radius + (bml_distance - bml_radius)

    # Randomly change angle of bml in relation ot bone center
    # angle += random.uniform(-0.35, 0.35) # Randomly change angle between -20 and +20 degrees
    # print('Angle: ' + str(angle))
    
    _rand_angle = random.randrange(45, 135)
    _rand_angle = _rand_angle if _rand_angle != 90 else 91
    new_angle = math.radians(_rand_angle)
    # rotate_angle_deg = math.degrees(angle - new_angle)
    rotate_angle_deg = 0
    # angle = new_angle
    

    src_bml_center = mask_helper.get_mask_center(src_bml)
    target_bone_center = mask_helper.get_mask_center(target_bone)
    bone_center = target_bone_center
    
    ## Create line to intersect with bone edges
    unit_vector = (math.cos(angle), math.sin(angle))
    vector = (unit_vector[0] * img_size, unit_vector[1] * img_size)
    projected_point = (int(bone_center[0] + vector[0]), int(bone_center[1] + vector[1]))
    
    ## Get bone edges + intersection point
    bone_edges = mask_helper.get_mask_edges(target_bone)
    edge_point = mask_helper.get_closest_edge_to_line(bone_edges, bone_center, projected_point, img_size)

    ## Find where bml center point should be
    bml_point = (
        int(edge_point[0] - (unit_vector[0] * bml_distance)),
        int(edge_point[1] - (unit_vector[1] * bml_distance)),
    )
    bml_diff_x = bml_point[0] - src_bml_center[0]
    bml_diff_y = bml_point[1] - src_bml_center[1]

    ########

    #### 3. Place bml on target image
    img, img_mask = synthesis.extract_mask_region_from_path(
        bml_path, bml_mask_path, 
        target_path, target_bone_mask_path,
        bml_diff_x, bml_diff_y,
        rotate_angle_deg)


    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_mask = cv2.cvtColor(img_mask, cv2.COLOR_BGR2GRAY)
    # pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # pil_img = pil_img.rotate(-45)
    # img = np.asarray(pil_img)


    cv2.imwrite(os.path.join(output_folder, filename + '.bmp'), img)
    cv2.imwrite(os.path.join(output_folder, filename + '_mask.bmp'), img_mask)
    
    # print('Wrote image:  ' + os.path.join(output_folder, filename + '.bmp'))

    ## Draw info to image (for easier testing)
    img = cv2.circle(img, 
        (int(bone_center[0]), int(bone_center[1])),
        5, (0,0,255), 4
        )
    img = mask_helper.draw_mask_contours(target_bone, img)
    ###### img = cv2.line(img, p1, p2, (0,0,0), 2)
    ##### img = cv2.circle(img, src_bml_center, 1, (255,0,0), 2)
    ##### img = cv2.circle(img, edge_point, 2, (0,255,255), 2) # Bml edge point
    # img = cv2.line(img, bone_center, projected_point, (255,0,0), 1)
    # img = cv2.circle(img, edge_point, 2, (0,0,255), 2)
    # img = cv2.circle(img, bml_point, 2, (255,0,0), 2)

    # cv2.imwrite(os.path.join(output_folder, filename + '_diagram.bmp'), img)
    

def main():
    main_1()

if __name__ == '__main__':
    main()