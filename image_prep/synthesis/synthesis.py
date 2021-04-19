import numpy as np
import cv2
import os
from PIL import Image
import mask_helper

def extract_mask_region(img, mask, target, target_mask, x_offset = 0, y_offset = 0, rotate = 0):
    
    # x_offset = -24
    # y_offset = -23

    # x_offset = -10
    # y_offset = -10
    # blur = 19
    # blur_sigma = 100

    blur = 29
    blur_sigma = 5

    blur = 3
    blur_sigma = 5
    
    

    #### Get new mask (before creating bml image)
    translated_mask = translate_image(mask, x_offset, y_offset)
    bone_center = mask_helper.get_mask_center(translated_mask)
    translated_mask = cv2.cvtColor(translated_mask, cv2.COLOR_GRAY2BGR).astype('float') / 255.
    pil_img = Image.fromarray(cv2.cvtColor((translated_mask * 255).astype('uint8'), cv2.COLOR_BGR2RGB))
    pil_img = pil_img.rotate(rotate, 0,0, (bone_center))
    translated_mask = np.asarray(pil_img).astype('float') / 255.

    target_mask_2 = cv2.cvtColor(target_mask, cv2.COLOR_GRAY2BGR).astype('float') / 255.
    translated_mask = translated_mask * target_mask_2 # Crop translated mask around target bone mask
    translated_mask = (translated_mask * 255).astype('uint8')
    # 
    # pil_img = Image.fromarray(cv2.cvtColor(translated_mask, cv2.COLOR_BGR2RGB))
    # pil_img = pil_img.rotate(-90, 0,0, bone_center)
    # translated_mask = np.asarray(pil_img)
    # cv2.cvtColor(translated_mask, cv2.COLOR_GRAY2BGR).astype('float') / 255.
    ####

    # mask = expand_mask(mask, 1, True)
    # cv2.imwrite('./output/mask_bml.bmp', mask)

    # Blur mask
    mask_blurred = cv2.GaussianBlur(mask, (blur, blur), blur_sigma)
    # Mix blurred mask with regular mask
    mask_blurred = cv2.addWeighted(mask_blurred, 0.7, mask, 0.3, 0)
    # Save image just for testing purposes
    # cv2.imwrite('./output/mask_bml_blurred.bmp', mask_blurred)    

    mask_blurred_3chan = cv2.cvtColor(mask_blurred, cv2.COLOR_GRAY2BGR).astype('float') / 255.
    img = img.astype('float') / 255.
    target = target.astype('float') / 255.

    # Crop image around mask
    # cropped_img = img
    cropped_img = img * mask_blurred_3chan


    

    # Translate mask region
    cropped_img = translate_image(cropped_img, x_offset, y_offset)
    mask_blurred_3chan_translated = translate_image(mask_blurred_3chan, x_offset, y_offset)

    # Rotate mask region
    pil_img = Image.fromarray(cv2.cvtColor((cropped_img * 255).astype('uint8'), cv2.COLOR_BGR2RGB))
    pil_img = pil_img.rotate(rotate, 0,0, bone_center)
    cropped_img = np.asarray(pil_img).astype('float') / 255.

    pil_img = Image.fromarray(cv2.cvtColor((mask_blurred_3chan_translated * 255).astype('uint8'), cv2.COLOR_BGR2RGB))
    pil_img = pil_img.rotate(rotate, 0,0, bone_center)
    mask_blurred_3chan_translated = np.asarray(pil_img).astype('float') / 255.
    #####

    # Crop the masked image around the bone mask of target image
    # target_mask = expand_mask(target_mask, 11, True)
    target_mask = expand_mask(target_mask, 1, True)

    # cv2.imwrite('./output/mask_bone.bmp', target_mask)

    target_mask_blurred = cv2.GaussianBlur(target_mask, (7, 7), 5)
    # Mix blurred mask with regular mask
    target_mask_blurred = cv2.addWeighted(target_mask_blurred, 2, target_mask, 1, 0)
    # cv2.imwrite('./output/mask_bone_blurred.bmp', target_mask_blurred)

    target_mask_blurred_3chan = cv2.cvtColor(target_mask_blurred, cv2.COLOR_GRAY2BGR).astype('float') / 255.
    double_cropped_img = cropped_img * target_mask_blurred_3chan

    # Set contrast and brightness
    # alpha=0.9
    beta=-0.25
    alpha = 1.0
    # beta=0.0
    target_mask_blurred_3chan = cv2.addWeighted(target_mask_blurred_3chan,alpha,np.zeros(target_mask_blurred_3chan.shape, target_mask_blurred_3chan.dtype),0,beta)
    ##

    # Combine everything
    # out  = target * (1 - mask_blurred_3chan_translated) + cropped_img
    # out  = target * (1 - mask_blurred_3chan_translated) + double_cropped_img
    out  = target * (1 - (mask_blurred_3chan_translated * target_mask_blurred_3chan)) + double_cropped_img
    
    # IF MANUAL
    # Crop around bone for 'manual' images
    out = out * target_mask_2
    ###########

    out = (out * 255).astype('uint8')

    return out, translated_mask

def extract_mask_region_from_path(img_path, mask_path, target_path, target_mask_path, x_offset = 0, y_offset = 0, rotate = 0):
    img = cv2.imread(img_path)
    mask = cv2.imread(mask_path, 0)
    target = cv2.imread(target_path)
    target_mask = cv2.imread(target_mask_path, 0)
    # target[:, :, 0] = 255
    # target[:, :, 1] = 0
    # target[:, :, 2] = 0

    return extract_mask_region(img, mask, target, target_mask, x_offset, y_offset, rotate)

def translate_image(img, x, y):
    height, width = img.shape[:2]     
    T = np.float32([[1, 0, x], [0, 1, y]]) 
    img_translation = cv2.warpAffine(img, T, (width, height)) 
    return img_translation

def expand_mask(img, expand = 0, inverse = False):
    if (expand == 0):
        return img

    result = cv2.GaussianBlur(img, (expand, expand), 0)
    # result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR).astype('float') / 255.
    result = result.astype('float') / 255.
    
    if (inverse == False):
        result =  np.ceil(result)
    else:
        result =  np.floor(result)

    result = (result * 255).astype('uint8')

    return result



def synthesize(bml_image_path, bml_mask_path, healthy_image_path, healthy_bone_mask_path, output_folder, output_filename):
    output = extract_mask_region_from_path(bml_image_path, bml_mask_path, healthy_image_path, healthy_bone_mask_path)
    cv2.imwrite(os.path.join(output_folder, output_filename + '.bmp'), output)
    

def main():
    img_path = '../../data/RawBml/data-384/train/9184588_v00_33.bmp'
    # 9184588_v00_33_mask
    # 9000099_v03_30_mask.bmp
    mask_path = '../../data/RawBml/data-384/train/9184588_v00_33_mask.bmp'
    target_path = '../../data/RawBml/data-lite-384/train/9014883_v00_25.bmp'
    target_mask_path = '../../data/BoneMasks/9014883_v00_25.bmp'
    output = extract_mask_region_from_path(img_path, mask_path, target_path, target_mask_path)

    cv2.imwrite('./output/target_synthetic.bmp', output)
    cv2.imwrite('./output/source.bmp', cv2.imread(img_path))
    # cv2.imwrite('./output/mask.bmp', cv2.imread(mask_path))
    cv2.imwrite('./output/target.bmp', cv2.imread(target_path))
    # cv2.imwrite('./output/target_mask.bmp', cv2.imread(target_mask_path))

if __name__ == '__main__':
    main()