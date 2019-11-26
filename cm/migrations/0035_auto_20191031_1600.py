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
# Generated by Django 2.2.1 on 2019-10-31 16:00

from django.db import migrations


def fix_button(apps, schema_editor):
    Action = apps.get_model('cm', 'Action')
    for action in Action.objects.filter(button='0'):
        action.button = None
        action.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cm', '0034_auto_20191029_1041'),
    ]

    operations = [
        migrations.RunPython(fix_button),
    ]
