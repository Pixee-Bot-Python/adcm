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
# Generated by Django 2.0.5 on 2018-08-29 10:20
# pylint: disable=line-too-long

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cm', '0002_auto_20180801_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='prototypeconfig',
            name='display_name',
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name='stageprototypeconfig',
            name='display_name',
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AlterField(
            model_name='bundle',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='component',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='prototype',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='prototypeconfig',
            name='type',
            field=models.CharField(choices=[('string', 'string'), ('text', 'text'), ('password', 'password'), ('json', 'json'), ('integer', 'integer'), ('float', 'float'), ('option', 'option'), ('boolean', 'boolean'), ('file', 'file')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stagecomponent',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='stageprototype',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='stageprototypeconfig',
            name='type',
            field=models.CharField(choices=[('string', 'string'), ('text', 'text'), ('password', 'password'), ('json', 'json'), ('integer', 'integer'), ('float', 'float'), ('option', 'option'), ('boolean', 'boolean'), ('file', 'file')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stageupgrade',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='upgrade',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
