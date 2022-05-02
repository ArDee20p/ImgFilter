from PIL import Image, ImageFilter, ImageEnhance
import shutil
import colorsys


def load_image(image_path):
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        print('Unable to load image')


def dupe_image(image_path, options):
    if options == 'copy':
        shutil.copyfile(image_path, image_path + '.copy')
    elif options == 'replace':
        shutil.copyfile(image_path + '.copy', image_path)


def get_default_slider():
    return {'color': 1, 'bright': 1, 'contrast': 1, 'sharp': 1}


def get_image_size(image):
    return image.width, image.height


# ENHANCERS
def apply_enhancers(image, image_path, slider):
    colorer = ImageEnhance.Color(image)
    image = colorer.enhance(slider['color'])
    brighter = ImageEnhance.Brightness(image)
    image = brighter.enhance(slider['bright'])
    contraster = ImageEnhance.Contrast(image)
    image = contraster.enhance(slider['contrast'])
    sharper = ImageEnhance.Sharpness(image)
    image = sharper.enhance(slider['sharp'])

    image.save(image_path)


# HUE [ inspired by: https://stackoverflow.com/questions/24874765 ]
def get_dominant_colors(image_path, colors_count=5):
    image = load_image(image_path)
    width, height = get_image_size(image)
    colors = image.getcolors(maxcolors=width * height)
    return sorted(colors, reverse=True)[:colors_count]


def apply_hue_shift(image_path, hue_angle):
    image = load_image(image_path)
    image = image.convert('RGB')
    width, height = get_image_size(image)
    ld = image.load()

    for i in range(width):
        for j in range(height):
            r, g, b = ld[i, j]
            h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
            h = (h + hue_angle / 360.0) % 1.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            ld[i, j] = (int(r * 255.9999), int(g * 255.9999), int(b * 255.9999))

    image.save(image_path)


# BLUR
def apply_blur(image_path, options):
    image = load_image(image_path)

    if options == "0":
        image = image.filter(ImageFilter.BLUR)
    elif options == "1":
        image = image.filter(ImageFilter.BoxBlur(1))
    elif options == "2":
        image = image.filter(ImageFilter.GaussianBlur)

    image.save(image_path)


# SHARPEN
def apply_sharpen(image_path, options):
    image = load_image(image_path)

    if options == "0":
        image = image.filter(ImageFilter.SHARPEN)
    elif options == "1":
        image = image.filter(ImageFilter.DETAIL)
    elif options == "2":
        image = image.filter(ImageFilter.UnsharpMask)

    image.save(image_path)


# EDGE ENHANCE
def apply_edge_enhance(image_path, options):
    image = load_image(image_path)

    if options == "0":
        image = image.filter(ImageFilter.EDGE_ENHANCE)
    elif options == "1":
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    elif options == "2":
        image = image.filter(ImageFilter.EMBOSS)
    elif options == "3":
        image = image.filter(ImageFilter.FIND_EDGES)
    elif options == "4":
        image = image.filter(ImageFilter.CONTOUR)

    image.save(image_path)


# SMOOTH
def apply_smooth(image_path, options):
    image = load_image(image_path)

    if options == "0":
        image = image.filter(ImageFilter.SMOOTH)
    elif options == "1":
        image = image.filter(ImageFilter.SMOOTH_MORE)

    image.save(image_path)


# ROTATE
def rotate_image(image_path, angle):
    image = load_image(image_path)
    image = image.rotate(angle)
    image.save(image_path)


# RESIZE
def resize_image(image_path, width, height):
    image = load_image(image_path)
    image = image.resize((width, height), Image.BICUBIC)
    image.save(image_path)


# CROP
def crop_image(image_path, start_x, start_y, end_x, end_y):
    image = load_image(image_path)
    image = image.crop((start_x, start_y, end_x, end_y))
    image.save(image_path)