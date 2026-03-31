from pathlib import Path
import os
import glob
# 获取当前脚本所在目录的绝对路径
project_dir = str(Path(__file__).parent.resolve())
QR_IMAGES = "{}static/images".format(project_dir.replace("src",''))
PUSH_PATH = "{}static/pic_content".format(project_dir.replace("src",''))
CHROME_PROFILE = "{}chrome_profile".format(project_dir.replace("src",''))
HEADLESS = True
BASE_URL = "https://www.imgurl.org"




