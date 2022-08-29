from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.views import View
from rest_framework.response import Response

from audit.cases.common import get_or_create_audit_obj
from audit.models import AuditLogOperationType, AuditObject, AuditOperation
from cm.models import GroupConfig, Host, ObjectConfig


def _get_obj_type(obj_type: str) -> str:
    if obj_type == "cluster object":
        return "service"
    elif obj_type == "service component":
        return "component"

    return obj_type


def _get_obj_name(obj: Model, obj_type: str) -> str:
    if obj_type == "service":
        obj_name = obj.display_name
        cluster = getattr(obj, "cluster")
        if cluster:
            obj_name = f"{cluster.name}/{obj_name}"
    elif obj_type == "component":
        obj_name = obj.display_name
        service = getattr(obj, "service")
        if service:
            obj_name = f"{service.display_name}/{obj_name}"
            cluster = getattr(service, "cluster")
            if cluster:
                obj_name = f"{cluster.name}/{obj_name}"
    else:
        obj_name = obj.name

    return obj_name


# pylint: disable-next=too-many-locals,too-many-branches,too-many-statements
def config_case(
        path: list[str, ...],
        view: View,
        response: Response,
        deleted_obj: Model,
) -> tuple[AuditOperation, AuditObject | None, str | None]:
    audit_operation = None
    audit_object = None
    operation_name = None

    match path:
        case ["config-log"]:
            audit_operation = AuditOperation(
                name=f"configuration {AuditLogOperationType.Update}d",
                operation_type=AuditLogOperationType.Update,
            )

            config = None
            if response:
                config = response.data.serializer.instance.obj_ref
            elif view.request.data.get("obj_ref"):
                config = ObjectConfig.objects.filter(pk=view.request.data["obj_ref"]).first()

            if config:
                object_type = ContentType.objects.get_for_model(config.object).name
                object_type = _get_obj_type(obj_type=object_type)
                object_name = _get_obj_name(obj=config.object, obj_type=object_type)

                audit_object = get_or_create_audit_obj(
                    object_id=config.object.pk,
                    object_name=object_name,
                    object_type=object_type,
                )
                if object_type == "adcm":
                    object_type = "ADCM"
                else:
                    object_type = object_type.capitalize()

                operation_name = f"{object_type} {audit_operation.name}"
            else:
                audit_object = None

        case ["group-config", group_config_pk, "config", _, "config-log"]:
            audit_operation = AuditOperation(
                name=f"configuration group {AuditLogOperationType.Update}d",
                operation_type=AuditLogOperationType.Update,
            )

            config = None
            if response:
                config = response.data.serializer.instance.obj_ref
                if getattr(config, "group_config", None):
                    config = config.group_config
            elif view.request.data.get("obj_ref"):
                config = ObjectConfig.objects.filter(pk=view.request.data["obj_ref"]).first()

            if not config:
                config = GroupConfig.objects.filter(pk=group_config_pk).first()

            if config:
                object_type = ContentType.objects.get_for_model(config.object).name
                object_type = _get_obj_type(object_type)
                object_name = _get_obj_name(obj=config.object, obj_type=object_type)

                audit_object = get_or_create_audit_obj(
                    object_id=config.object.pk,
                    object_name=object_name,
                    object_type=object_type,
                )
                object_type = object_type.capitalize()
                if isinstance(config, GroupConfig):
                    object_type = config.name

                operation_name = f"{object_type} {audit_operation.name}"
            else:
                audit_object = None

        case ["group-config"]:
            if view.action == "create":
                operation_type = AuditLogOperationType.Create
            elif view.action in {"update", "partial_update"}:
                operation_type = AuditLogOperationType.Update
            else:
                operation_type = AuditLogOperationType.Delete

            audit_operation = AuditOperation(
                name=f"configuration group {operation_type}d",
                operation_type=operation_type,
            )
            if response:
                if view.action == "destroy":
                    deleted_obj: GroupConfig
                    obj = deleted_obj
                else:
                    obj = response.data.serializer.instance

                object_type = _get_obj_type(obj.object_type.name)
                object_name = _get_obj_name(obj=obj.object, obj_type=object_type)
                audit_object = get_or_create_audit_obj(
                    object_id=obj.object.id,
                    object_name=object_name,
                    object_type=object_type,
                )
                operation_name = f"{obj.name} {audit_operation.name}"
            else:
                audit_object = None

        case ["group-config", group_config_pk]:
            if view.action in {"update", "partial_update"}:
                operation_type = AuditLogOperationType.Update
            else:
                operation_type = AuditLogOperationType.Delete

            audit_operation = AuditOperation(
                name=f"configuration group {operation_type}d",
                operation_type=operation_type,
            )
            if response:
                if view.action == "destroy":
                    deleted_obj: GroupConfig
                    obj = deleted_obj
                else:
                    obj = response.data.serializer.instance
            else:
                obj = GroupConfig.objects.filter(pk=group_config_pk).first()

            if obj:
                object_type = _get_obj_type(obj.object_type.name)
                object_name = _get_obj_name(obj=obj.object, obj_type=object_type)
                audit_object = get_or_create_audit_obj(
                    object_id=obj.object.id,
                    object_name=object_name,
                    object_type=object_type,
                )
                operation_name = f"{obj.name} {audit_operation.name}"
            else:
                audit_object = None

        case ["group-config", config_group_pk, "host"]:
            config_group = GroupConfig.objects.get(pk=config_group_pk)
            audit_operation = AuditOperation(
                name=f"host added to {config_group.name} configuration group",
                operation_type=AuditLogOperationType.Update,
            )
            object_type = _get_obj_type(config_group.object_type.name)
            object_name = _get_obj_name(obj=config_group.object, obj_type=object_type)
            audit_object = get_or_create_audit_obj(
                object_id=config_group.pk,
                object_name=object_name,
                object_type=object_type,
            )

            fqdn = None
            if response:
                fqdn = response.data["fqdn"]
            elif "id" in view.request.data:
                host = Host.objects.filter(pk=view.request.data["id"]).first()
                if host:
                    fqdn = host.fqdn

            if fqdn:
                audit_operation.name = f"{fqdn} {audit_operation.name}"

        case ["group-config", config_group_pk, "host", host_pk]:
            config_group = GroupConfig.objects.get(pk=config_group_pk)
            obj = Host.objects.get(pk=host_pk)
            audit_operation = AuditOperation(
                name=f"{obj.name} host removed from {config_group.name} configuration group",
                operation_type=AuditLogOperationType.Update,
            )
            object_type = _get_obj_type(config_group.object_type.name)
            object_name = _get_obj_name(obj=config_group.object, obj_type=object_type)
            audit_object = get_or_create_audit_obj(
                object_id=config_group.pk,
                object_name=object_name,
                object_type=object_type,
            )

    return audit_operation, audit_object, operation_name
