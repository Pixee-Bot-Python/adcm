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

from django.db import migrations


def copy_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    OldProfile = apps.get_model('cm', 'UserProfile')
    NewProfile = apps.get_model('rbac', 'UserProfile')
    for user in User.objects.all():
        try:
            op = OldProfile.objects.get(login=user.username)
            np = NewProfile(user=user, profile=op.profile)
        except OldProfile.DoesNotExist:
            np = NewProfile(user=user, profile="")
        np.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_profiles),
    ]
