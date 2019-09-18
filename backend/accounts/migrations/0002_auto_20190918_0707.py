# Generated by Django 2.2.5 on 2019-09-18 07:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='groups',
        ),
        migrations.AddField(
            model_name='user',
            name='group',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='auth.Group'),
            preserve_default=False,
        ),
    ]
