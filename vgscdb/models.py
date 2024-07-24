from django.db import models

# Create your models here.

class Target(models.Model):
    name = models.CharField(max_length=100)

    vgscdb_id = models.CharField(max_length=100)

    description = models.TextField()

    orgnism = models.TextField()

    uniprot_id = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Compound(models.Model):
    vgscdb_id = models.CharField(max_length=100, blank=True)

    name = models.TextField(blank=True)

    pubchem_cid = models.CharField(max_length=100, blank=True)

    iupac_name = models.TextField(blank=True)

    molecular_formula = models.TextField(blank=True)

    molecular_weight = models.TextField(blank=True)

    ic50ec50 = models.TextField(blank=True)

    target = models.ManyToManyField(Target)

    Bindingsite = models.TextField(blank=True)

    orgnism = models.TextField(blank=True)

    uniprot_name = models.TextField(blank=True)

    uniprot_id = models.TextField(blank=True)

    smiles = models.TextField(blank=True)

    inchi = models.TextField(blank=True)

    inchi_key = models.TextField(blank=True)

    article_doi = models.TextField(blank=True)

    pmid = models.TextField(blank=True)

    authors = models.TextField(blank=True)
    
    institution = models.TextField(blank=True)

    pdb_id = models.TextField(blank=True)

    def __str__(self):
        return self.name
