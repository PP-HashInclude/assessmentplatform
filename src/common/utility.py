import os
import tempfile
from pdf2image import convert_from_path
from PIL import Image

from pdf2jpg import pdf2jpg


def getQPaperData(qPaperFile):
    filecontent = ""

    with open(qPaperFile, "r") as qfile:
        filecontent = qfile.readlines()
    
    return filecontent

def convert_pdf(file_path, output_path):
    # save temp image files in temp dir, delete them after we are finished
    with tempfile.TemporaryDirectory() as temp_dir:
        # convert pdf to multiple image
        images = convert_from_path(file_path, output_folder=temp_dir, poppler_path='C:\\data\\Programs\\poppler-0.68.0\\bin')
        # save images to temporary directory
        temp_images = []
        for i in range(len(images)):
            image_path = f'{temp_dir}/{i}.jpg'
            images[i].save(image_path, 'JPEG')
            temp_images.append(image_path)
            images[i].close()

        # read images into pillow.Image
        imgs = list(map(Image.open, temp_images))

        # find minimum width of images
        min_img_width = min(i.width for i in imgs)
        # find total height of all images
        total_height = 0
        for i, img in enumerate(imgs):
            total_height += imgs[i].height
        # create new image object with width and total height
        merged_image = Image.new(imgs[0].mode, (min_img_width, total_height))
        # paste images together one by one
        y = 0
        for img in imgs:
            merged_image.paste(img, (0, y))
            y += img.height
        # save merged image
        #merged_image.save(output_path)
        base_filename = os.path.splitext(os.path.basename(file_path))[0] + '.jpg'
        print (base_filename)
        merged_image.save(output_path + "\\" + base_filename)
        return output_path + "\\" + base_filename

def convert_pdf2(filename, output_path):
    with tempfile.TemporaryDirectory() as path:
        images_from_path = convert_from_path(filename, output_folder=path, poppler_path='C:\\data\\Programs\\poppler-0.68.0\\bin')
    
    base_filename = os.path.splitext(os.path.basename(filename))[0] + '.jpg'

    for page in images_from_path:
        page.save(os.path.join(output_path, base_filename), 'JPEG')

def convert_pdf3(filename, output_path):
    inputpath = filename
    outputpath = output_path
    # To convert single page
    #result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="1")
    #print(result)

    # To convert multiple pages
    #result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="1,0,3")
    #print(result)

    # to convert all pages
    result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="ALL")
    #print(result)
    imageslist = result[0]["output_jpgfiles"]

    images = [Image.open(x) for x in imageslist]
    widths, heights = zip(*(i.size for i in images))
    
    min_img_width = min(i.width for i in images)

    total_height = 0
    for i, img in enumerate(images):
            total_height += images[i].height

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))
    new_imy = Image.new('RGB', (min_img_width, total_height))

    x_offset = 0
    y_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]

        new_imy.paste(im, (0, y_offset))
        y_offset += im.height
    
    new_im.save('test.jpg')
    new_imy.save('testy.jpg')
