# Generated by Django 5.0.7 on 2024-07-21 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vgscdb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compound',
            name='category',
        ),
        migrations.RemoveField(
            model_name='target',
            name='source',
        ),
        migrations.RemoveField(
            model_name='target',
            name='pdb_id',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Source',
        ),
    ]
