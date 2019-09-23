# Generated by Django 2.2.5 on 2019-09-23 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mime', models.CharField(max_length=4)),
                ('path', models.CharField(max_length=255)),
                ('data', models.BinaryField()),
            ],
        ),
    ]
