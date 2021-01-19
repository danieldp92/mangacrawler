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


def chapter_validator(chapters):
    if not isinstance(chapters, list):
        raise Exception("Invalid chapter param type")

    new_chapters = []
    for chapter in chapters:
        if "-" in chapter:
            chapters_split = chapter.split("-")
            if len(chapters_split) != 2:
                raise Exception("Invalid multi-chapter selection used. Use the following formula -> "
                                "startchapter-endchapter (es 1-100)")

            start_chapter = int(chapters_split[0])
            end_chapter = int(chapters_split[1])

            if end_chapter < start_chapter:
                raise Exception("Invalid multi-chapter selection used. The endchapter must be greater or equal to the "
                                "startchapter")

            for single_chapter in range(start_chapter, end_chapter+1):
                # If it is not an integer, an exception will be thrown
                new_chapters.append(single_chapter)
        else:
            chapter = int(chapter)
            new_chapters.append(chapter)

    return new_chapters