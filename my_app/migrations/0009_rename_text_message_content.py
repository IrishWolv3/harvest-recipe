# Generated by Django 5.1.6 on 2025-04-23 02:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0008_message_alter_ingredienttrip_unique_together_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='text',
            new_name='content',
        ),
    ]
