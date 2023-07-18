# Generated by Django 4.2.1 on 2023-05-22 16:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_photo_usercomfirmation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='user_photos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['img', 'jpg', 'jpeg', 'heic', 'heif'])]),
        ),
    ]