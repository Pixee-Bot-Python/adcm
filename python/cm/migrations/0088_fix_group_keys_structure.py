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

# Generated by Django 3.2.13 on 2022-05-20 12:52

from typing import Dict

from django.db import migrations, models


def create_group_keys(
    config_spec: dict,
    group_keys: Dict[str, bool] = None,
    custom_group_keys: Dict[str, bool] = None,
):
    """
    Returns a map of fields that are included in a group,
    as well as a map of fields that cannot be included in a group
    """
    if group_keys is None:
        group_keys = {}
    if custom_group_keys is None:
        custom_group_keys = {}
    for k, v in config_spec.items():
        if v["type"] == "group":
            value = None
            if "activatable" in v["limits"]:
                value = False
            group_keys.setdefault(k, {"value": value, "fields": {}})
            custom_group_keys.setdefault(k, {"value": v["group_customization"], "fields": {}})
            create_group_keys(v["fields"], group_keys[k]["fields"], custom_group_keys[k]["fields"])
        else:
            group_keys[k] = False
            custom_group_keys[k] = v["group_customization"]
    return group_keys, custom_group_keys


def get_config_spec(apps, group):
    """Return spec for config"""

    PrototypeConfig = apps.get_model("cm", "PrototypeConfig")
    Cluster = apps.get_model("cm", "Cluster")
    ClusterObject = apps.get_model("cm", "ClusterObject")
    ServiceComponent = apps.get_model("cm", "ServiceComponent")
    HostProvider = apps.get_model("cm", "HostProvider")
    spec = {}
    object_type = group.object_type.model
    if object_type == "cluster":
        obj = Cluster.objects.get(id=group.object_id)
    elif object_type == "clusterobject":
        obj = ClusterObject.objects.get(id=group.object_id)
    elif object_type == "servicecomponent":
        obj = ServiceComponent.objects.get(id=group.object_id)
    elif object_type == "hostprovider":
        obj = HostProvider.objects.get(id=group.object_id)
    else:
        raise models.ObjectDoesNotExist
    for field in PrototypeConfig.objects.filter(prototype=obj.prototype, action__isnull=True).order_by("id"):
        group_customization = field.group_customization
        if group_customization is None:
            group_customization = obj.prototype.config_group_customization
        field_spec = {
            "type": field.type,
            "group_customization": group_customization,
            "limits": field.limits,
        }
        if field.subname == "":
            if field.type == "group":
                field_spec.update({"fields": {}})
            spec[field.name] = field_spec
        else:
            spec[field.name]["fields"][field.subname] = field_spec
    return spec


def fix_group_keys(group_keys, spec):
    """Fix `group_keys` structure"""

    correct_group_keys = {}
    for field, info in spec.items():
        if info["type"] == "group":
            correct_group_keys[field] = {}
            if "activatable" in info["limits"]:
                correct_group_keys[field]["value"] = False
            else:
                correct_group_keys[field]["value"] = None
            correct_group_keys[field]["fields"] = {}
            for key in info["fields"].keys():
                correct_group_keys[field]["fields"][key] = group_keys[field][key]
        else:
            correct_group_keys[field] = group_keys[field]
    return correct_group_keys


def fix_group_keys_structure(apps, schema_editor):
    """Fix `group_keys` structure for `group-config`"""

    GroupConfig = apps.get_model("cm", "GroupConfig")
    ConfigLog = apps.get_model("cm", "ConfigLog")

    for group in GroupConfig.objects.all():
        if group.config is not None:
            spec = get_config_spec(apps, group)
            _, custom_group_keys = create_group_keys(spec)
            current_config_log = ConfigLog.objects.get(id=group.config.current)
            group_keys = current_config_log.attr["group_keys"]
            correct_group_keys = fix_group_keys(group_keys, spec)
            current_config_log.attr["group_keys"] = correct_group_keys
            current_config_log.attr["custom_group_keys"] = custom_group_keys
            current_config_log.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cm", "0087_maintenance_mode"),
    ]

    operations = [migrations.RunPython(fix_group_keys_structure)]
