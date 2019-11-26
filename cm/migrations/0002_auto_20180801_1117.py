# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Generated by Django 2.0.5 on 2018-08-01 11:17
# pylint: disable=line-too-long

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StageUpgrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=160)),
                ('description', models.CharField(blank=True, max_length=160)),
                ('min_version', models.CharField(max_length=80)),
                ('max_version', models.CharField(max_length=80)),
                ('state_available', models.TextField(blank=True)),
                ('state_on_success', models.CharField(blank=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Upgrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=160)),
                ('description', models.CharField(blank=True, max_length=160)),
                ('min_version', models.CharField(max_length=80)),
                ('max_version', models.CharField(max_length=80)),
                ('state_available', models.TextField(blank=True)),
                ('state_on_success', models.CharField(blank=True, max_length=64)),
                ('bundle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cm.Bundle')),
            ],
        ),
        migrations.AlterField(
            model_name='prototypeconfig',
            name='type',
            field=models.CharField(choices=[('string', 'string'), ('password', 'password'), ('json', 'json'), ('integer', 'integer'), ('float', 'float'), ('option', 'option'), ('boolean', 'boolean'), ('file', 'file')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stageprototypeconfig',
            name='type',
            field=models.CharField(choices=[('string', 'string'), ('password', 'password'), ('json', 'json'), ('integer', 'integer'), ('float', 'float'), ('option', 'option'), ('boolean', 'boolean'), ('file', 'file')], max_length=16),
        ),
    ]
