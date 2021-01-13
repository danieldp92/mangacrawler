import os
from PIL import Image


def convert_to_pdf(img_folder_path, pdf_name, output_dir=""):
    imagelist = []

    # Get the path of all images inside the folder
    for file in os.listdir(img_folder_path):
        if file.endswith(".jpg") or file.endswith(".png"):
            imagelist.append(os.path.join(img_folder_path, file))

    im1 = Image.open(imagelist[0])
    im1.load()
    im1 = image_validator(im1)

    im_list = []
    for i in range(1, len(imagelist)):
        im = Image.open(imagelist[i])
        im.load()
        im = image_validator(im)

        im_list.append(im)

    pdf_path = os.path.join(output_dir, pdf_name)

    im1.save(pdf_path, "PDF", resolution=100.0, save_all=True, quality=10, append_images=im_list)


def image_validator(img):
    if img.mode != "L" and img.mode != "RGB":
        if img.mode == "RGBA":
            rgb = Image.new('RGB', img.size, (255, 255, 255))  # white background
            rgb.paste(img, mask=img.split()[3])
            img = rgb
        else:
            img = img.convert("L")
    return img