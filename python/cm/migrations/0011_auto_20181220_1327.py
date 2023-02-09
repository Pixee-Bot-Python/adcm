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

# Generated by Django 2.0.5 on 2018-12-20 13:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cm", "0010_auto_20181212_1213"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="button",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="stageaction",
            name="button",
            field=models.BooleanField(default=False),
        ),
    ]
