# Generated by Django 4.1.7 on 2023-03-14 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_message_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
    ]
