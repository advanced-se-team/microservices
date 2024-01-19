import os
import glob
import time

import fitz
from loguru import logger
import cv2
from pdf2image import convert_from_path
import os
import cv2
from paddleocr import PPStructure, draw_structure_result, save_structure_res



# 将pdf转换为图片
def pdf_to_image(pdfPath, imagePath):
    pdfDoc = fitz.open(pdfPath)
    logger.info(f'处理文件：{pdfDoc}, 文件页面数：{len(pdfDoc)}')
    for pg in range(len(pdfDoc)):
        page = pdfDoc[pg]
        rotate = int(0)
        zoom_x = 6
        zoom_y = 6
        # pix = page.getPixmap(alpha=False)
        # pix = page.get_pixmap(alpha=False)# 默认是720*x尺寸

        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat, dpi=None, colorspace='rgb', alpha=False)

        # if not os.path.exists(imagePath):
        #     os.makedirs(imagePath)
        pix.save(f'{imagePath}\\images_{pg}.jpg')     #将图片写入指定的文件夹内

# 切割图片, y2 += 120覆盖说明
def rectangle_select(imageDir, x1, y1, x2, y2, save_path: str = "picdir.png"):
    image = cv2.imread(imageDir)
    # 左上角坐标
    x1, y1 = abs(x1), abs(y1)
    # 右下角坐标
    x2, y2 = abs(x2), abs(y2)
    # 保存图片
    cv2.imwrite(save_path, image[y1:y2, x1:x2])
    # 圈选区域
    # cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 4)
    # 截取区域
    return image[y1:y2, x1:x2]

# 选取图表
def pptool(img_path, savepath):
    table_engine = PPStructure(show_log=True)

    img = cv2.imread(img_path)
    result = table_engine(img)
    save_structure_res(result, savepath, os.path.basename(img_path).split('.')[0])

    for line in result:
        line.pop('img')
        print(line)

    from PIL import Image

    font_path = 'doc/fonts/simfang.ttf'  # PaddleOCR下提供字体包
    image = Image.open(img_path).convert('RGB')
    # im_show = draw_structure_result(image, result, font_path=font_path)
    # im_show = Image.fromarray(im_show)
    # im_show.save('result.jpg')

if __name__ == '__main__': # 解析图片和表格 时间较长，不继续演示

    PDFDir = 'icse2023a.pdf'

    #pdf每页截图代码
    sTime = time.time()
    # pdf_to_image('1.pdf', 'F:\image\\output\\')
    pdf_to_image(PDFDir, 'inputPic\\')
    # pdf_to_TextBlocks('1.pdf', 'F:\image\pdftxt.txt')
    eTime = time.time()
    s = eTime - sTime
    print('花费的时间为：%.2f秒' % (s))

    # 指定文件夹路径和文件名模式
    folder_path = 'inputPic\\'
    file_pattern = '*.jpg'  # 匹配所有以 .txt 结尾的文件

    # 使用glob.glob()函数匹配文件名模式
    matching_files = glob.glob(os.path.join(folder_path, file_pattern))

    # 遍历匹配的文件列表
    for file in matching_files:
        pg = int(file.replace("inputPic\images_","").replace(".jpg", "")) + 1
        logger.info(f'当前处理第{pg}页')
        savePath = 'output\\' + str(pg) + '\\'
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        pptool(file, savePath)


