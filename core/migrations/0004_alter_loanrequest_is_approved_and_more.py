# Generated by Django 5.2.3 on 2025-06-15 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_loanrequest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="loanrequest",
            name="is_approved",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="loanrequest",
            name="reason",
            field=models.CharField(max_length=255),
        ),
    ]
