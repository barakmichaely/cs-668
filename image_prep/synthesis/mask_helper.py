import numpy as np
import cv2
from scipy import ndimage
from skimage.measure import regionprops
import sys
import os
sys.path.append(os.path.abspath(os.path.join('..', 'resize')))
import resize
import line_helper
import math

def get_mask_area(mask):
    area = cv2.countNonZero(mask)
    return area


def get_mask_rect(mask):
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    y1, y2 = np.where(rows)[0][[0, -1]]
    x1, x2 = np.where(cols)[0][[0, -1]]

    return { 'y1': y1, 'y2': y2, 'x1': x1, 'x2': x2 }

def draw_rect(img, rect):
    color = (255, 0, 0)
    _img = cv2.line( img, (rect['x1'], rect['y1']), (rect['x1'], rect['y2']), color, 1 )
    _img = cv2.line( _img, (rect['x1'], rect['y1']), (rect['x2'], rect['y1']), color, 1 )
    _img = cv2.line( _img, (rect['x1'], rect['y2']), (rect['x2'], rect['y2']), color, 1 )
    _img = cv2.line( _img, (rect['x2'], rect['y2']), (rect['x2'], rect['y1']), color, 1 )
    return _img



def get_mask_center(mask):
    # convert the grayscale image to binary image
    ret,thresh = cv2.threshold(mask,127,255,0)
    # calculate moments of binary image
    M = cv2.moments(thresh)
    # calculate x,y coordinate of center
    cX = 0 if (M["m00"] == 0) else int(M["m10"] / M["m00"])
    cY = 0 if (M["m00"] == 0) else int(M["m01"] / M["m00"])

    center = (cX, cY)
    return center

def draw_center(mask, bg = None):
    if (bg is None):
        bg = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    center = get_mask_center(mask)
    # img = cv2.cvtColor(bg, cv2.COLOR_GRAY2BGR)
    img = cv2.circle(bg, ( int(center[0]), int(center[1])), 2, (0, 50, 255), 3)
    return img



def get_mask_contours(mask):
    ret, thresh = cv2.threshold(mask, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_mask_edges(mask):
    edges = []
    contours = get_mask_contours(mask)
    for c in contours[0]:
        edges.append((c[0][0], c[0][1]))
    return edges

def draw_mask_contours(mask, bg, color = (255,255,0)):
    if (bg is None):
        bg = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    contours = get_mask_contours(mask)
    img = cv2.drawContours(bg, contours, -1, color, 1)
    

    return img


def _get_line_max(bone_center, bml_center, img_size):
    min_x = 0
    max_x = img_size
    min_y = 0
    max_y = img_size

    # Figure out where to start and end line on the x-axis
    if (bml_center[0] < bone_center[0]):
        min_x = 0
        max_x = bone_center[0]
    else:
        min_x = bone_center[0]
        max_x = img_size

    # Figure out where to start and end line on the y-axis
    if (bml_center[1] < bone_center[1]):
        min_y = 0
        max_y = bone_center[1]
    else:
        min_y = bone_center[1]
        max_y = img_size

    return min_x, max_x, min_y, max_y

def get_distance(x1, x2, y1, y2):
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))

def get_closest_edge_to_line(edges, p1, p2, img_size):
    min_x, max_x, min_y, max_y = _get_line_max(p1, p2, img_size)

    # print('min: (' + str(min_x) + ',' + str(min_y) + ') -- ' + '(' + str(max_x) + ',' + str(max_y) + ')')

    # Calculate distance from bml_center to edge of bone (on the projected line)
    _closest_edge_distance = max_x
    closest_edge_point = (0, 0)
    for point in edges:
        for x in range(min_x, max_x):
            y = line_helper.solve_for_y(p1, p2, x)
            if (y is None or y < min_y or y > max_y):
                continue
            # Find contact point between bone edge and projected line
            # distance = math.sqrt(pow(x - p[0], 2) + pow(y - p[1], 2))
            distance = get_distance(x, point[0], y, point[1])
            if (distance < _closest_edge_distance):
                # print('Got here')
                _closest_edge_distance = distance
                closest_edge_point = point

    return closest_edge_point

def get_bml_distance(bone_mask, bml_mask):
    img_size = len(bone_mask)
    bone_center = get_mask_center(bone_mask)
    bml_center = get_mask_center(bml_mask)
    # angle in radians
    angle = math.atan2(bml_center[1] - bone_center[1], bml_center[0] - bone_center[0])
    edges = get_mask_edges(bone_mask)
    min_x, max_x, min_y, max_y = _get_line_max(bone_center, bml_center, len(bone_mask))


    cv2.imwrite(os.path.join('./output_data', 'og.bmp'), bone_mask)

    # ## Create line to intersect with bone edges
    # unit_vector = (math.cos(angle), math.sin(angle))
    # vector = (unit_vector[0] * img_size, unit_vector[1] * img_size)
    # projected_point = (int(bone_center[0] + vector[0]), int(bone_center[1] + vector[1]))

    # Calculate distance from bml_center to edge of bone (on the projected line)
    _closest_edge_distance = max_x
    closest_edge_point = (0, 0)
    
    # closest_edge_point = get_closest_edge_to_line(edges, bone_center, (0, 384), img_size)

    for p in edges:
        for x in range(min_x, max_x):
            y = line_helper.solve_for_y(bone_center, bml_center, x)
            if (y is None or y < min_y or y > max_y):
                continue
            # Find contact point between bone edge and projected line
            # distance = math.sqrt(pow(x - p[0], 2) + pow(y - p[1], 2))
            distance = get_distance(x, p[0], y, p[1])
            if (distance < _closest_edge_distance):
                _closest_edge_distance = distance
                closest_edge_point = p
    ###
    # print('Bone center: ' + str(bone_center))
    # print('Projecteed point: ' + str(projected_point))
    # print('BML Center: ' + str(bml_center) + ', Edge Point: ' + str(closest_edge_point))
    bml_distance = get_distance(bml_center[0], closest_edge_point[0], bml_center[1], closest_edge_point[1])
    bone_center_distance = get_distance(bone_center[0], closest_edge_point[0], bone_center[1], closest_edge_point[1])

    #################
    # Find bml radius
    bml_edges = get_mask_edges(bml_mask)
    _bml_closest_edge_distance = max_x
    _bml_closest_edge_point = (0, 0)
    for p in bml_edges:
        for x in range(min_x, max_x):
            y = line_helper.solve_for_y(bone_center, bml_center, x)
            if (y is None or y < min_y or y > max_y):
                continue
            d = get_distance(x, p[0], y, p[1])
            if (d < _bml_closest_edge_distance):
                _bml_closest_edge_distance = distance
                _bml_closest_edge_point = p
    #
    bml_radius = get_distance(bml_center[0], _bml_closest_edge_point[0], bml_center[1], _bml_closest_edge_point[1])
    #################


    return angle, bml_distance, bone_center_distance, bml_radius



def calculate_bml_distance(bone_mask, bml_mask, bg):
    bone_center = get_mask_center(bone_mask)

    img = draw_center(bone_mask, bg)
    img = draw_mask_contours(bone_mask, img)
    
    # img = bml_mask
    bml_center = get_mask_center(bml_mask)
    img = draw_center(bml_mask, img)
    img = draw_mask_contours(bml_mask, img, (255,100,100))

    # Get line
    min_x = 0
    max_x = len(img)
    min_y = 0
    max_y = len(img)

    # Figure out where to start and end line on the x-axis
    if (bml_center[0] < bone_center[0]):
        min_x = 0
        max_x = bone_center[0]
    else:
        min_x = bone_center[0]
        max_x = len(img)

    # Figure out where to start and end line on the y-axis
    if (bml_center[1] < bone_center[1]):
        min_y = 0
        max_y = bone_center[1]
    else:
        min_y = bone_center[1]
        max_y = len(img)
    

    line_y1 = int(round(line_helper.solve_for_y(bone_center, bml_center, min_x)))
    line_y2 = int(round(line_helper.solve_for_y(bone_center, bml_center, max_x)))

    img = cv2.line(img, (min_x, line_y1), (max_x, line_y2), (0,50,255) , 1)

    # Find bone edge point closest to line
    edges = get_mask_edges(bone_mask)
    closest_edge = (0,0)
    closest_edge_distance = max_x
    for p in edges:
        for x in range(min_x, max_x):
            y = line_helper.solve_for_y(bone_center, bml_center, x)
            
            if (y is None or y < min_y or y > max_y):
                continue

            # line_point = (x, y)
            distance = math.sqrt(pow(x - p[0], 2) + pow(y - p[1], 2))
            if (distance < closest_edge_distance):
                closest_edge_distance = distance
                closest_edge = p

    img = cv2.circle(img, closest_edge, 2, (0,255,0), 3)



    return img 



def main():
    
    # resize.resize_image('../../data/BoneMasks/bone/Phase3/9129226_v00_17.bmp', '../../data/BoneMasks/9129226_v00_17.bmp', 384, 384)    
    # return

    
    
    
    src_img2 = cv2.imread('../../data/RawBml/data-384/train/9002116_v00_11.bmp')
    src_bml2 = cv2.imread('../../data/RawBml/data-384/train/9002116_v00_11_mask.bmp', 0)
    src_bone2 = cv2.imread('../../data/BoneMasks/9002116_v00_11.bmp', 0)

    src_img3 = cv2.imread('../../data/RawBml/data-384/train/9129226_v00_17.bmp')
    src_bml3 = cv2.imread('../../data/RawBml/data-384/train/9129226_v00_17_mask.bmp', 0)
    src_bone3 = cv2.imread('../../data/BoneMasks/9129226_v00_17.bmp', 0)

    

    # return
    distance1 = calculate_bml_distance(src_bone, src_bml, src_img)
    cv2.imwrite('./output/masks/distance.bmp', distance1)

    distance2 = calculate_bml_distance(src_bone2, src_bml2, src_img2)
    cv2.imwrite('./output/masks/distance2.bmp', distance2)

    distance3 = calculate_bml_distance(src_bone3, src_bml3, src_img3)
    cv2.imwrite('./output/masks/distance3.bmp', distance3)


    # mask1 = cv2.imread('../../data/BoneMasks/9014883_v00_25.bmp', 0)
    

    # return
    # area = get_mask_area(mask1)
    # center = draw_center(mask1)
    # cv2.imwrite('./output/masks/target_bone_center.bmp', center)

    # source_bml_center = draw_center(source_bml_mask)
    # cv2.imwrite('./output/masks/source_bml_center.bmp', source_bml_center)

    
    


if __name__ == '__main__':
    main()