import os
import sys
import django
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

CACTUS = "https://cactus.nci.nih.gov/chemical/structure/{0}/{1}"

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

def read_tsv_files_from_directory(directory_path):
    # 初始化一个空的DataFrame来存储所有文件的数据
    combined_data = pd.DataFrame()
    
    # 遍历目录下的所有文件
    for filename in os.listdir(directory_path):
        # 检查文件是否以 .tsv 结尾
        if filename.endswith('.tsv'):
            file_path = os.path.join(directory_path, filename)
            # 读取TSV文件
            data = pd.read_csv(file_path, delimiter='\t')
            data.columns = data.columns.str.strip()
            # 将文件的数据追加到 combined_data
            combined_data = pd.concat([combined_data, data], ignore_index=True)
    
    return combined_data

def calculate_formula_and_molecular_weight(smiles):
    # 解析 SMILES
    molecule = Chem.MolFromSmiles(smiles)
    
    if molecule is None:
        return None, None  # 如果解析失败，返回 None

    # 计算化学式
    formula = Chem.rdMolDescriptors.CalcMolFormula(molecule)
    
    # 计算相对分子质量
    molecular_weight = Descriptors.MolWt(molecule)

    return formula, molecular_weight

# 获取iupac_name
def cid_to_iupac(cid):
    # 使用CID获取IUPAC名称
    url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName/JSON'
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception("Error fetching IUPAC name from CID")
    
    properties = response.json().get('PropertyTable', {}).get('Properties', [])
    if not properties:
        raise Exception("No properties found for given CID")
    
    iupac_name = properties[0].get('IUPACName', '')
    return iupac_name

# 获取对应Target
def get_or_create_target(target_name):
    target, created = Target.objects.get_or_create(name=target_name)
    return target

def fetch_iupac_name(pubchem_cid):
    try:
        return pubchem_cid, cid_to_iupac(pubchem_cid)
    except Exception as e:
        return pubchem_cid, None

def save_to_database(data):
    ind = 1
    pubchem_cids = data['PubChem CID of Ligand'].dropna().unique()

    # 使用ThreadPoolExecutor并行获取IUPAC名称
    iupac_names = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_cid = {executor.submit(fetch_iupac_name, cid): cid for cid in pubchem_cids}
        for future in as_completed(future_to_cid):
            cid = future_to_cid[future]
            try:
                pubchem_cid, iupac_name = future.result()
                iupac_names[pubchem_cid] = iupac_name
            except Exception as exc:
                print(f'Error fetching IUPAC name for CID {cid}: {exc}')
    
    # 逐行读取
    for index, row in data.iterrows():
        TargetName = row.get('Target Name', '').strip()
        LigandSMILES = row.get('Ligand SMILES', '')
        LigandInChI = row.get('Ligand InChI', '')
        LigandInChIKey = row.get('Ligand InChI Key', '')
        IC50 = row.get('IC50 (nM)', '')
        ArticleDOI = row.get('Article DOI', '')
        Authors = row.get('Authors', '')
        Institution = row.get('Institution', '')
        PubChemCIDofLigand = str(row.get('PubChem CID of Ligand', ''))
        Name = row.get('BindingDB Ligand Name', '')
        pmid = row.get('PMID', '')
        pdbid = row.get('PDB ID(s) for Ligand-Target Complex', '')
        
        # 取出无文献参考数据
        if pd.isna(ArticleDOI) or not ArticleDOI.strip():
            continue

        target = get_or_create_target(TargetName)
        formula, molecular_weight = calculate_formula_and_molecular_weight(LigandSMILES)
        iupac_name = iupac_names.get(PubChemCIDofLigand.strip(), None)
        
        compound = Compound.objects.create(
            vgscdb_id=ind,
            smiles=LigandSMILES,
            pubchem_cid=PubChemCIDofLigand.strip() if not pd.isna(PubChemCIDofLigand) else None,
            inchi=LigandInChI[6:] if LigandInChI and len(LigandInChI) > 6 else None,
            inchi_key=LigandInChIKey,
            ic50ec50=IC50 if not pd.isna(IC50) else None,
            article_doi=ArticleDOI if not pd.isna(ArticleDOI) else None,
            authors=Authors if not pd.isna(Authors) else None,
            institution=Institution if not pd.isna(Institution) else None,
            name = Name if not pd.isna(Name) else None,
            pmid = pmid if not pd.isna(pmid) else None,
            pdb_id = pdbid if not pd.isna(pdbid) else None,
            iupac_name = iupac_name if not pd.isna(LigandSMILES) else None,
            molecular_formula = formula,
            molecular_weight = round(molecular_weight, 3),
        )
        compound.target.set([target])
        ind = ind + 1

def import_tsv_to_django(tsv_file_path):
    full_path = os.path.join(BASE_DIR, "data")
    data = read_tsv_files_from_directory(full_path)
    save_to_database(data)

def find_target(compound_id):
    compound = Compound.objects.get(vgscdb_id=compound_id)

    # 获取该化合物关联的所有目标对象
    targets = compound.target.all()

    # 打印目标对象的信息
    for target in targets:
        print(target)  

if __name__ == '__main__':
    print("BASE_DIR:", BASE_DIR)
    print("DJANGO_SETTINGS_MODULE:", os.getenv('DJANGO_SETTINGS_MODULE'))
    import_tsv_to_django('Nav1.10.tsv')
