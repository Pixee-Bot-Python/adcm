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

# Generated by Django 2.0.5 on 2018-06-08 14:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Action",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=160)),
                (
                    "type",
                    models.CharField(choices=[("task", "task"), ("job", "job")], max_length=16),
                ),
                ("script", models.CharField(max_length=160)),
                (
                    "script_type",
                    models.CharField(
                        choices=[("ansible", "ansible"), ("task_generator", "task_generator")],
                        max_length=16,
                    ),
                ),
                ("state_on_success", models.CharField(blank=True, max_length=64)),
                ("state_on_fail", models.CharField(blank=True, max_length=64)),
                ("state_available", models.TextField(blank=True)),
                ("params", models.TextField(blank=True)),
                ("log_files", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Bundle",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=160)),
                ("version", models.CharField(max_length=80)),
                ("hash", models.CharField(max_length=64)),
                ("description", models.CharField(blank=True, max_length=160)),
                ("date", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Cluster",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=80, unique=True)),
                ("description", models.CharField(blank=True, max_length=160)),
                ("state", models.CharField(default="created", max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name="ClusterObject",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("state", models.CharField(default="created", max_length=64)),
                (
                    "cluster",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Cluster"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Component",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=160)),
                ("description", models.CharField(blank=True, max_length=160)),
                ("params", models.TextField(blank=True)),
                ("constraint", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="ConfigLog",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("config", models.TextField()),
                ("date", models.DateTimeField(auto_now=True)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Host",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("fqdn", models.CharField(max_length=160, unique=True)),
                ("state", models.CharField(default="created", max_length=64)),
                (
                    "cluster",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="cm.Cluster",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HostComponent",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("state", models.CharField(default="created", max_length=64)),
                (
                    "cluster",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Cluster"),
                ),
                (
                    "component",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Component"),
                ),
                (
                    "host",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Host"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="JobLog",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("task_id", models.PositiveIntegerField(default=0)),
                ("action_id", models.PositiveIntegerField()),
                ("selector", models.TextField()),
                ("log_files", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "created"),
                            ("running", "running"),
                            ("success", "success"),
                            ("failed", "failed"),
                        ],
                        max_length=16,
                    ),
                ),
                ("date", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="ObjectConfig",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("current", models.PositiveIntegerField()),
                ("previous", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Prototype",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("service", "service"), ("cluster", "cluster"), ("host", "host")],
                        max_length=16,
                    ),
                ),
                ("name", models.CharField(max_length=160)),
                ("version", models.CharField(max_length=80)),
                ("description", models.CharField(blank=True, max_length=160)),
                (
                    "bundle",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Bundle"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PrototypeConfig",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=160)),
                ("subname", models.CharField(blank=True, max_length=160)),
                ("default", models.TextField(blank=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("string", "string"),
                            ("integer", "integer"),
                            ("float", "float"),
                            ("option", "option"),
                            ("boolean", "boolean"),
                        ],
                        max_length=16,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("limits", models.TextField(blank=True)),
                ("required", models.BooleanField(default=True)),
                (
                    "prototype",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Prototype"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StageAction",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=160)),
                (
                    "type",
                    models.CharField(choices=[("task", "task"), ("job", "job")], max_length=16),
                ),
                ("script", models.CharField(max_length=160)),
                (
                    "script_type",
                    models.CharField(
                        choices=[("ansible", "ansible"), ("task_generator", "task_generator")],
                        max_length=16,
                    ),
                ),
                ("state_on_success", models.CharField(blank=True, max_length=64)),
                ("state_on_fail", models.CharField(blank=True, max_length=64)),
                ("state_available", models.TextField(blank=True)),
                ("params", models.TextField(blank=True)),
                ("log_files", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="StageComponent",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=160)),
                ("description", models.CharField(blank=True, max_length=160)),
                ("params", models.TextField(blank=True)),
                ("constraint", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="StagePrototype",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("service", "service"), ("cluster", "cluster"), ("host", "host")],
                        max_length=16,
                    ),
                ),
                ("name", models.CharField(max_length=160)),
                ("version", models.CharField(max_length=80)),
                ("description", models.CharField(blank=True, max_length=160)),
            ],
        ),
        migrations.CreateModel(
            name="StagePrototypeConfig",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=160)),
                ("subname", models.CharField(blank=True, max_length=160)),
                ("default", models.TextField(blank=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("string", "string"),
                            ("integer", "integer"),
                            ("float", "float"),
                            ("option", "option"),
                            ("boolean", "boolean"),
                        ],
                        max_length=16,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("limits", models.TextField(blank=True)),
                ("required", models.BooleanField(default=True)),
                (
                    "prototype",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.StagePrototype"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskLog",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("action_id", models.PositiveIntegerField()),
                ("object_id", models.PositiveIntegerField()),
                ("selector", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "created"),
                            ("running", "running"),
                            ("success", "success"),
                            ("failed", "failed"),
                        ],
                        max_length=16,
                    ),
                ),
                ("date", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("login", models.CharField(max_length=32, unique=True)),
                ("profile", models.TextField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="stageprototype",
            unique_together={("name", "version")},
        ),
        migrations.AddField(
            model_name="stagecomponent",
            name="prototype",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.StagePrototype"),
        ),
        migrations.AddField(
            model_name="stageaction",
            name="prototype",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.StagePrototype"),
        ),
        migrations.AddField(
            model_name="hostcomponent",
            name="service",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Prototype"),
        ),
        migrations.AddField(
            model_name="host",
            name="config",
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to="cm.ObjectConfig"),
        ),
        migrations.AddField(
            model_name="host",
            name="prototype",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Prototype"),
        ),
        migrations.AddField(
            model_name="configlog",
            name="obj_ref",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.ObjectConfig"),
        ),
        migrations.AddField(
            model_name="component",
            name="prototype",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Prototype"),
        ),
        migrations.AddField(
            model_name="clusterobject",
            name="config",
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to="cm.ObjectConfig"),
        ),
        migrations.AddField(
            model_name="clusterobject",
            name="prototype",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Prototype"),
        ),
        migrations.AddField(
            model_name="cluster",
            name="config",
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to="cm.ObjectConfig"),
        ),
        migrations.AddField(
            model_name="cluster",
            name="prototype",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Prototype"),
        ),
        migrations.AlterUniqueTogether(
            name="bundle",
            unique_together={("name", "version")},
        ),
        migrations.AddField(
            model_name="action",
            name="prototype",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="cm.Prototype"),
        ),
        migrations.AlterUniqueTogether(
            name="stageprototypeconfig",
            unique_together={("prototype", "name", "subname")},
        ),
        migrations.AlterUniqueTogether(
            name="stagecomponent",
            unique_together={("prototype", "name")},
        ),
        migrations.AlterUniqueTogether(
            name="stageaction",
            unique_together={("prototype", "name")},
        ),
        migrations.AlterUniqueTogether(
            name="prototypeconfig",
            unique_together={("prototype", "name", "subname")},
        ),
        migrations.AlterUniqueTogether(
            name="prototype",
            unique_together={("bundle", "name", "version")},
        ),
        migrations.AlterUniqueTogether(
            name="hostcomponent",
            unique_together={("host", "service", "component")},
        ),
        migrations.AlterUniqueTogether(
            name="component",
            unique_together={("prototype", "name")},
        ),
        migrations.AlterUniqueTogether(
            name="clusterobject",
            unique_together={("cluster", "prototype")},
        ),
        migrations.AlterUniqueTogether(
            name="action",
            unique_together={("prototype", "name")},
        ),
    ]
