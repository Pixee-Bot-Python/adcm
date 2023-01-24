# Generated by Django 3.2.16 on 2023-01-24 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0002_alter_auditobject_object_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='operation_name',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='operation_result',
            field=models.CharField(choices=[('success', 'success'), ('fail', 'fail'), ('denied', 'denied')], max_length=1000),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='operation_type',
            field=models.CharField(choices=[('create', 'create'), ('update', 'update'), ('delete', 'delete')], max_length=1000),
        ),
        migrations.AlterField(
            model_name='auditobject',
            name='object_name',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='auditobject',
            name='object_type',
            field=models.CharField(choices=[('prototype', 'prototype'), ('cluster', 'cluster'), ('service', 'service'), ('component', 'component'), ('host', 'host'), ('provider', 'provider'), ('bundle', 'bundle'), ('adcm', 'adcm'), ('user', 'user'), ('group', 'group'), ('role', 'role'), ('policy', 'policy')], max_length=1000),
        ),
        migrations.AlterField(
            model_name='auditsession',
            name='login_result',
            field=models.CharField(choices=[('success', 'success'), ('wrong password', 'wrong password'), ('account disabled', 'account disabled'), ('user not found', 'user not found')], max_length=1000),
        ),
    ]
