import io
import random
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def fig2im(fig):
    """Generates a PIL Image from a Matplotlib figure
    
    :param fig: input figure
    :type Matplotlib figure
    
    :rtype: PIL image instance
    :return: returns a PIL RGB image from the provided figure
    """
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = np.frombuffer(buff.getvalue(), dtype=np.uint8)
        
    w, h = fig.canvas.get_width_height()
    im_data = data.reshape((int(h), int(w), -1))
    
    return Image.fromarray(np.uint8(im_data)).convert('RGB')

def get_text_for_cell(mode, target_num):
    """Generates the text that should appear in the cell. It can be the number
    of the corresponding color or a simple math operation that gives that number
    as a result
    
    :param mode: a string in ('n', 'a', 's'). Specifies how to express the color
                that should go in the cell:
                    'n': the number of the color. Default value
                    'a': an addition that gives the number of the color as result
                    's': a subtraction that gives the number of the color as result
    :type mode: str
    :param target_num: the number of the color that corresponds to this cell

    
    :rtype: str
    :return: the string to print in the cell
    """ 
    assert mode in ('n', 'a', 's')
    
    if mode == 'n':
        text = str(target_num)
    elif mode == 'a':
        first_operand = random.randint(0, target_num)
        second_operand = target_num - first_operand
        text = f"{first_operand}+{second_operand}"
    elif mode == 's':
        first_operand = random.randint(target_num, 9)
        second_operand = first_operand - target_num
        text = f"{first_operand} - {second_operand}"
    
    return text

def generate_color_by_number_sheet(input_image, color_list, mode='n'):
    """Generates our color-by-number sheet from an image. This function is an absolte mess
    since it was my first time working with matplotlib beyond plotting simple graphs...
    
    :param input_image: input pixelated image
    :type input_image: PIL Image instance
    :param color_list: list of colors to use
    :type color_list: list
    :param mode: a string in ('n', 'a', 's'). Specifies how to express the color
                that should go in the cell:
                    'n': the number of the color. Default value
                    'a': an addition that gives the number of the color as result
                    's': a subtraction that gives the number of the color as result
    :type mode: str
    
    :rtype: PIL Image instance
    :return: returns a ready to print color-by-number sheet
    """     
    assert mode in ('n', 'a', 's')
    
    sheet_size = input_image.size[0]
    
    # See if pure white is in colors. We will not print anything for those cells
    try:
        white_index = color_list.index([255, 255, 255])
    except:
        white_index = -1
        
    # First, create the table
    if mode == 'n':
        fontsize = 28
    else:
        fontsize = 20

    np_image = np.array(input_image).flatten()

    table = plt.figure(figsize=(sheet_size, sheet_size), dpi=150, tight_layout={"h_pad": 0.04167, "w_pad": 0.04167, "pad": 1.08, "rect": (0, 0, 1, 1)});
    for i in range(1, sheet_size*sheet_size + 1):
        ax = table.add_subplot(sheet_size, sheet_size, i, aspect='equal')
        ax.tick_params(labelbottom=False, labelleft=False)
        for axis in ['top','bottom','left','right']:
            ax.spines[axis].set_linewidth(4)

        color_index = np_image[i-1]
        if color_index == white_index:
            cell_text = ''
        else:
            tgt_color_index = color_index + 1 if color_index < white_index else color_index
            cell_text = get_text_for_cell(mode, tgt_color_index)
        ax.text(0.5, 0.5, cell_text, fontsize=fontsize, ha='center')

    table_image = fig2im(table)
    
    table.clear()
    
    # Next, create the color legend
    cell_width = 636
    cell_height = 110
    swatch_width = 144
    margin = 20
    topmargin = 80

    nrows = len(color_list)

    width = cell_width * 4 + 2 * margin
    height = cell_height * nrows + margin + topmargin
    dpi = 150

    legend, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi);
    #legend.subplots_adjust(margin/width, margin/height,
    #                        (width-margin)/width, (height-topmargin)/height)
    ax.set_xlim(0, cell_width * 4)
    ax.set_ylim(cell_height * nrows, -cell_height/2.)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_axis_off()

    for color_index, color in enumerate(color_list):
        row = color_index
        y = row * cell_height

        swatch_start_x = margin #cell_width * col
        text_pos_x = margin + 1.25*swatch_width #cell_width * col + swatch_width + 7

        if color_index == white_index:
            cell_text = 'Empty cells'
        else:
            cell_text = str(color_index + 1 if color_index < white_index else color_index)

        ax.text(text_pos_x, y + 0.3*cell_height, cell_text, fontsize=28,
                    horizontalalignment='left',
                    verticalalignment='center')

        ax.add_patch(
                Rectangle(xy=(swatch_start_x, y), width=swatch_width,
                          height=0.6*cell_height, facecolor=np.array(color)/255, edgecolor='0'))

    plt.tight_layout();

    legend_image = fig2im(legend)
    
    legend.clear()
    
    # Finally, compose both elements together
    table_img_w, table_img_h = table_image.size
    legend_img_w, legend_img_h = legend_image.size

    offset = 10

    color_sheet = Image.new('RGBA', (table_img_w, table_img_h + legend_img_h + offset), (255, 255, 255, 255))
    color_sheet.paste(table_image)
    color_sheet.paste(legend_image, (0, table_img_h + offset))

    return color_sheet
