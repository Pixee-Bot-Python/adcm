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

# Generated by Django 2.0.5 on 2019-01-24 13:44

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        ('cm', '0013_auto_20190116_1143'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='joblog',
            name='date',
        ),
        migrations.RemoveField(
            model_name='tasklog',
            name='date',
        ),
        migrations.AddField(
            model_name='joblog',
            name='finish_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 1, 12, 0, 0, 100500, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='joblog',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 1, 12, 0, 0, 100500, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tasklog',
            name='finish_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 1, 12, 0, 0, 100500, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tasklog',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 1, 12, 0, 0, 100500, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
