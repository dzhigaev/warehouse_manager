# Generated by Django 4.0 on 2022-03-20 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_rrtoken_expiary_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rrtoken',
            name='expiary_date',
            field=models.IntegerField(),
        ),
    ]