# Generated by Django 5.0.7 on 2024-07-22 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vgscdb', '0005_alter_compound_bindingsite_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='compound',
            name='name',
            field=models.TextField(blank=True),
        ),
    ]
