from PIL import Image
import math
import numpy as np

def crop_central(input_image):
    """Takes an input image and crops a centered square region
    
    :param input_image: initial image
    :type input_image: PIL Image instance
    
    :rtype: PIL Image instance
    :return: cropped image with equal width and height
    """
    min_dim = min(input_image.size)
    if input_image.size[0] == input_image.size[1]: # Square image
        return(input_image)
    elif input_image.size[0] > input_image.size[1]: # Horizontal image
        x_shift = (input_image.size[0]-min_dim)/2
        y_shift = 0
    else:                                           # Vertical image
        x_shift = 0
        y_shift = (input_image.size[1]-min_dim)/2
    
    return input_image.crop((x_shift, y_shift, min_dim + x_shift, min_dim + y_shift))

def limit_colors(input_image, n_colors):
    """Takes an input image and creates a paletted version with the specified number of colors
    
    :param input_image: initial image
    :type input_image: PIL Image instance
    :param n_colors: desired number of colors
    :type n_colors: int
    
    :rtype: PIL Image instance
    :return: palletted image with the desired number of colors
    """
    mode = input_image.mode
    
    assert mode in ("P", "RGB", "RGBA", "1", "L", "LA")
    
    if mode == 'P':
        current_n_colors = len(input_image.getcolors())
                   
        if current_n_colors > n_colors:
            rgb_im = input_image.convert('RGB')
            paletted_im = rgb_im.quantize(colors=n_colors, dither=None, method=1, kmeans=1)
        else:
            paletted_im = input_image
    elif mode == 'RGBA':
        # Make image transparent white anywhere it is transparent
        rgba = np.array(input_image)
        rgba[rgba[...,-1]==0] = [255,255,255,1]
        
        rgb_im = Image.fromarray(rgba).convert('RGB')
        
        paletted_im = rgb_im.quantize(colors=n_colors, dither=None, method=1, kmeans=1)
    elif mode == 'LA':
        # Make image transparent white anywhere it is transparent
        ga = np.array(input_image)
        ga[ga[...,-1]==0] = [255,1]
        
        rgb_im = Image.fromarray(ga).convert('RGB')
        paletted_im = rgb_im.quantize(colors=n_colors, dither=None, method=1, kmeans=1)
    elif mode == '1':
        rgb_im = input_image.convert('RGB')
        paletted_im = rgb_im.quantize(colors=n_colors, dither=None, method=1, kmeans=1)
    else:
        paletted_im = input_image.quantize(colors=n_colors, dither=None, method=1, kmeans=1)
        
    # Check number of resulting colors
    current_n_colors = len(paletted_im.getcolors())
    if current_n_colors < n_colors:
        print(f'A total of {n_colors} was requested, but the number of colors in provided image is {current_n_colors}. Using that.')
        n_colors = current_n_colors
           
    palette = paletted_im.getpalette()
    colors = []
    for idx in range(n_colors):
        colors.append(palette[idx*3:idx*3+3])

    colors = np.minimum(17 * (np.array(colors) // 17 + 1), [255, 255, 255])
    return paletted_im, colors.tolist()

def pixelate_image(input_image, target_size=32):
    """Resample input image to desired resolution creating a pixelated version
    
    :param input_image: initial image
    :type input_image: PIL Image instance
    :param target_size: desired output size in pixels, defaults to 32
    :type target_size: int
    
    :rtype: PIL Image instance
    :return: pixelated version of input image of size target_size X target_size
    """
    return input_image.resize((target_size, target_size), Image.HAMMING, reducing_gap = math.sqrt(3))

