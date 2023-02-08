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

# Generated by Django 3.2.15 on 2022-11-21 17:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditobject",
            name="object_type",
            field=models.CharField(
                choices=[
                    ("prototype", "prototype"),
                    ("cluster", "cluster"),
                    ("service", "service"),
                    ("component", "component"),
                    ("host", "host"),
                    ("provider", "provider"),
                    ("bundle", "bundle"),
                    ("adcm", "adcm"),
                    ("user", "user"),
                    ("group", "group"),
                    ("role", "role"),
                    ("policy", "policy"),
                ],
                max_length=16,
            ),
        ),
    ]
