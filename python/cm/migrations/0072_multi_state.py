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

# Generated by Django 3.2 on 2021-08-12 07:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cm", "0071_messagetemplate"),
    ]

    operations = [
        migrations.AddField(
            model_name="adcm",
            name="_multi_state",
            field=models.JSONField(db_column="multi_state", default=dict),
        ),
        migrations.AddField(
            model_name="cluster",
            name="_multi_state",
            field=models.JSONField(db_column="multi_state", default=dict),
        ),
        migrations.AddField(
            model_name="clusterobject",
            name="_multi_state",
            field=models.JSONField(db_column="multi_state", default=dict),
        ),
        migrations.AddField(
            model_name="host",
            name="_multi_state",
            field=models.JSONField(db_column="multi_state", default=dict),
        ),
        migrations.AddField(
            model_name="hostprovider",
            name="_multi_state",
            field=models.JSONField(db_column="multi_state", default=dict),
        ),
        migrations.AddField(
            model_name="servicecomponent",
            name="_multi_state",
            field=models.JSONField(db_column="multi_state", default=dict),
        ),
    ]
