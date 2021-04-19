import typing
from PIL import Image, ImageDraw, ImageColor
import numpy as np
import os
from pathlib import Path


############
### CLASSES
############

class MaskMetadata:
    case_name = ""
    case_prefix = ""
    direction = ""
    image_width = 0
    image_height = 0
    start_slice = 0
    end_slice = 0

    def to_string(self):
        return '''
        Case number: {}
        Prefix: {}
        Direction: {}
        Image width: {}
        Image Height: {}
        Start slice: {}
        End Slice: {}
        '''.format(
            self.case_name, 
            self.case_prefix, 
            self.direction,
            self.image_width,
            self.image_height,
            self.start_slice,
            self.end_slice
            )

class Coordinate:
    y = 0
    x1 = 0
    x2 = 0

    def to_string(self):
        print(str(self.y) + " " + str(self.x1) + "." + str(self.x2))

class SliceData:
    slice_number = 0
    coordinates: typing.List[Coordinate] = []

    def __init__(self):
        self.slice_number = 0
        self.coordinates = []


##############
## Definitions
##############

# Main method
def generate_mask_images(filePath, fileName, outputFolder):
    file = open(filePath, 'r') 
    file_lines = file.readlines()
    metadata = extract_mask_metadata(file_lines)
    # print(metadata.to_string())
    slices = []
    

    #### Extract slices
    _got_last_slice = False
    while (_got_last_slice == False and len(file_lines) > 0):
        try:
            slice = extract_slice_mask(file_lines)
            
            if (slice == None): 
                continue

            slices.append(slice)
        except:
            print('Unable to parse slice. Skipping.')
            continue
        
        # Stop if reached last slice (to avoid over-parsing errors)
        if (slice.slice_number >= metadata.end_slice):
            _got_last_slice = True
            # print("---- End of Slices ---")
            break

    
    #### Save images
    Path(outputFolder).mkdir(parents=True, exist_ok=True) # Create directory if it doesn't exist
    extension = ".tiff"
    for s in slices:
        num_string = f"{s.slice_number:03}"
        path = os.path.join(outputFolder, fileName + "_" + num_string + "_mask" + extension)
        image = draw_slice_image(s, metadata)
        image.save(path)

    print("Done saving mask images to: " + outputFolder)


    

def draw_slice_image(slice: SliceData, meta: MaskMetadata):
    im = Image.new('RGB', (meta.image_width, meta.image_height), (0, 0, 0))
    image_array = np.zeros((meta.image_width, meta.image_height))
 
    for c in slice.coordinates:
        for idx in range(c.x1, c.x2 + 1):
            image_array[meta.image_height - c.y, idx] = 255

    im = Image.fromarray(image_array)
    # im.show()
    return im


# Gets a single slice's mask info
def extract_slice_mask(lines: list):
    slice = SliceData()
    slice.slice_number = -1 

    # Parse slice number safely
    while (slice.slice_number == -1):
        try:
            slice.slice_number = int( lines.pop(0).strip() )
            break
        except:
            print("Didn't find slice number at position")

        # Parsing didn't work right, don't parse this slice
        if (lines[0] == '{'):
            return None

    
    coordinate_lines = []
    _found_first_bracket = False
    _found_last_bracket = False

    # Extract raw lines
    while (_found_last_bracket == False):
        if (len(lines) == 0):
            break

        # Remove line from array
        line = lines.pop(0) 

        # Find first line with bracket to start parsing
        if (line.strip() == "{"):
            _found_first_bracket = True
            continue
            
        if (_found_first_bracket == False):
            continue
        
        # Find last bracket to stop
        if (line.strip() == "}"):
            _found_last_bracket = True
            break

        # Start parsing coordinates
        coordinate_lines.append(line.strip())

    # Get coordinates from lines
    for line in coordinate_lines:
        slice.coordinates.extend(_extract_coordinates(line))
    
    return slice
    

def _extract_coordinates(line):
    # Logic: 
    #   1. Extract first number as y
    #   2. For every pair after first number, create separate coordinate using the same y
    values = []
    
    # Get coordinate groups
    pairs: list = line.split(" ")
    for p in pairs: 
        p = p.strip()
    
    y = int(pairs[0]) # Define y value
    pairs.remove(pairs[0])

    # Create coordinate from each group
    for p in pairs:
        x1, x2 = p.split(".")
        c = Coordinate()
        c.y = y
        c.x1 = int(x1)
        c.x2 = int(x2)
        values.append(c)


    return values
        



# Gets file metadata
def extract_mask_metadata(lines: list):
    meta = MaskMetadata()
    meta.case_name = lines.pop(0).strip()
    meta.case_prefix = lines.pop(0).strip()
    meta.direction = lines.pop(0).strip()
    lines.pop(0).strip() # Skip this next line (not sure why)
    meta.image_width = int( lines.pop(0).strip() )
    meta.image_height = int( lines.pop(0).strip() )
    meta.start_slice = int( lines.pop(0).strip() )
    meta.end_slice = int( lines.pop(0).strip() )
    lines.pop(0).strip() # <- "Femur" line
    return meta