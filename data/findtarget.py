from vgscdb.models import Compound, Target

import os
import csv
import sys
import django
import pandas as pd

# 获取当前脚本所在目录的路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取 Django 项目的根目录
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# 将 Django 项目的根目录添加到 Python 路径中
sys.path.append(BASE_DIR)

# 设置 Django 设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vgscproject.settings")
django.setup()

# 查询特定的化合物，例如通过 ID 或其他唯一标识符
compound_id = 1  # 替换为你要查询的化合物 ID
compound = Compound.objects.get(id=compound_id)

# 获取该化合物关联的所有目标对象
targets = compound.target.all()

# 打印目标对象的信息
for target in targets:
    print(target)

def find_target(compound_id):
    compound = Compound.objects.get(id=compound_id)

    # 获取该化合物关联的所有目标对象
    targets = compound.target.all()

    # 打印目标对象的信息
    for target in targets:
        print(target)  
    


import os
import csv
import sys
import django
import pandas as pd

# 获取当前脚本所在目录的路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取 Django 项目的根目录
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# 将 Django 项目的根目录添加到 Python 路径中
sys.path.append(BASE_DIR)

# 设置 Django 设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vgscproject.settings")
django.setup()

from vgscdb.models import Compound, Target

def read_tsv(file_path):
    data = pd.read_csv(file_path, delimiter='\t')
    # 清理列名，去除多余的空格
    data.columns = data.columns.str.strip()
    return data

def get_or_create_target(target_name):
    target, created = Target.objects.get_or_create(name=target_name)
    return target

def save_to_database(data):
    for index, row in data.iterrows():
        TargetName = row.get('TargetName', '')
        LigandSMILES = row.get('LigandSMILES', '')
        LigandInChI = row.get('LigandInChI', '')
        LigandInChIKey = row.get('LigandInChIKey', '')
        IC50 = row.get('IC50', '')
        ArticleDOI = row.get('ArticleDOI', '')
        Authors = row.get('Authors', '')
        Institution = row.get('Institution', '')
        PubChemCIDofLigand = row.get('PubChemCIDofLigand', '')
        
        targetid = get_or_create_target('Sodium channel protein type 1 subunit alpha')
        
        compound = Compound.objects.create(
            vgscdb_id=index + 1,
            smiles=LigandSMILES,
            pubchem_cid=PubChemCIDofLigand if not pd.isna(PubChemCIDofLigand) else None,
            inchi=LigandInChI[6:] if LigandInChI and len(LigandInChI) > 6 else None,
            inchi_key=LigandInChIKey,
            ic50ec50=IC50 if not pd.isna(IC50) else None,
            article_doi=ArticleDOI if not pd.isna(ArticleDOI) else None,
            authors=Authors if not pd.isna(Authors) else None,
            institution=Institution if not pd.isna(Institution) else None,
        )
        compound.target.set([targetid])

def import_tsv_to_django(tsv_file_path):
    full_path = os.path.join(BASE_DIR, "data", tsv_file_path)
    data = read_tsv(full_path)
    save_to_database(data)

if __name__ == '__main__':
    print("BASE_DIR:", BASE_DIR)
    print("DJANGO_SETTINGS_MODULE:", os.getenv('DJANGO_SETTINGS_MODULE'))
    import_tsv_to_django('Nav1.tsv')
