import os
import django
import sys

# 获取当前脚本所在目录的路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取 Django 项目的根目录
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# 将 Django 项目的根目录添加到 Python 路径中
sys.path.append(BASE_DIR)

# 设置 Django 设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vgscproject.settings")
django.setup()

from vgscdb.models import Compound

def delete_all_compounds():
    Compound.objects.all().delete()
    print("All Compound objects have been deleted.")

if __name__ == '__main__':
    delete_all_compounds()