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

# Generated by Django 2.0.5 on 2019-02-19 10:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cm', '0017_auto_20190220_1137'),
    ]

    operations = [
        migrations.CreateModel(
            name='ADCM',
            fields=[
                (
                    'id',
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
                ),
                ('name', models.CharField(choices=[('ADCM', 'ADCM')], max_length=16, unique=True)),
                (
                    'config',
                    models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='cm.ObjectConfig'),
                ),
            ],
        ),
        migrations.AlterField(
            model_name='prototype',
            name='type',
            field=models.CharField(
                choices=[
                    ('adcm', 'adcm'),
                    ('service', 'service'),
                    ('cluster', 'cluster'),
                    ('host', 'host'),
                    ('provider', 'provider'),
                ],
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name='stageprototype',
            name='type',
            field=models.CharField(
                choices=[
                    ('adcm', 'adcm'),
                    ('service', 'service'),
                    ('cluster', 'cluster'),
                    ('host', 'host'),
                    ('provider', 'provider'),
                ],
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name='adcm',
            name='prototype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cm.Prototype'),
        ),
    ]
