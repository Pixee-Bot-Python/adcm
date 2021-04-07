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
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group, Permission
from django.db import models

from cm.errors import AdcmEx

PROTO_TYPE = (
    ('adcm', 'adcm'),
    ('service', 'service'),
    ('component', 'component'),
    ('cluster', 'cluster'),
    ('host', 'host'),
    ('provider', 'provider'),
)


LICENSE_STATE = (
    ('absent', 'absent'),
    ('accepted', 'accepted'),
    ('unaccepted', 'unaccepted'),
)


def get_model_by_type(object_type):
    if object_type == 'adcm':
        return ADCM
    if object_type == 'cluster':
        return Cluster
    elif object_type == 'provider':
        return HostProvider
    elif object_type == 'service':
        return ClusterObject
    elif object_type == 'component':
        return ServiceComponent
    elif object_type == 'host':
        return Host
    else:
        # This function should return a Model, this is necessary for the correct
        # construction of the schema.
        return Cluster


class ADCMManager(models.Manager):
    def get(self, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except ObjectDoesNotExist:
            if not hasattr(self.model, '__error_code__'):
                raise AdcmEx('NO_MODEL_ERROR_CODE', f'model: {self.model.__name__}') from None
            msg = '{} {} does not exist'.format(self.model.__name__, kwargs)
            raise AdcmEx(self.model.__error_code__, msg) from None


class ADCMModel(models.Model):
    objects = models.Manager()
    obj = ADCMManager()

    class Meta:
        abstract = True


class JSONField(models.Field):
    def db_type(self, connection):
        return 'text'

    def from_db_value(self, value, expression, connection):
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise AdcmEx(
                    'JSON_DB_ERROR',
                    msg=f"Not correct field format '{expression.field.attname}'") from None
        return value

    def get_prep_value(self, value):
        if value is not None:
            return str(json.dumps(value))
        return value

    def to_python(self, value):
        if value is not None:
            return json.loads(value)
        return value

    def value_to_string(self, obj):
        return self.value_from_object(obj)


class Bundle(ADCMModel):
    name = models.CharField(max_length=160)
    version = models.CharField(max_length=80)
    version_order = models.PositiveIntegerField(default=0)
    edition = models.CharField(max_length=80, default='community')
    license = models.CharField(max_length=16, choices=LICENSE_STATE, default='absent')
    license_path = models.CharField(max_length=160, default=None, null=True)
    license_hash = models.CharField(max_length=64, default=None, null=True)
    hash = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now=True)

    __error_code__ = 'BUNDLE_NOT_FOUND'

    class Meta:
        unique_together = (('name', 'version', 'edition'),)


class Upgrade(ADCMModel):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    min_version = models.CharField(max_length=80)
    max_version = models.CharField(max_length=80)
    from_edition = JSONField(default=['community'])
    min_strict = models.BooleanField(default=False)
    max_strict = models.BooleanField(default=False)
    state_available = JSONField(default=[])
    state_on_success = models.CharField(max_length=64, blank=True)

    __error_code__ = 'UPGRADE_NOT_FOUND'


MONITORING_TYPE = (
    ('active', 'active'),
    ('passive', 'passive'),
)


class Prototype(ADCMModel):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    type = models.CharField(max_length=16, choices=PROTO_TYPE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, default=None)
    path = models.CharField(max_length=160, default='')
    name = models.CharField(max_length=160)
    display_name = models.CharField(max_length=160, blank=True)
    version = models.CharField(max_length=80)
    version_order = models.PositiveIntegerField(default=0)
    required = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    constraint = JSONField(default=[0, '+'])
    requires = JSONField(default=[])
    bound_to = JSONField(default={})
    adcm_min_version = models.CharField(max_length=80, default=None, null=True)
    monitoring = models.CharField(max_length=16, choices=MONITORING_TYPE, default='active')
    description = models.TextField(blank=True)

    __error_code__ = 'PROTOTYPE_NOT_FOUND'

    def __str__(self):
        return str(self.name)

    class Meta:
        unique_together = (('bundle', 'type', 'parent', 'name', 'version'),)


class ObjectConfig(ADCMModel):
    current = models.PositiveIntegerField()
    previous = models.PositiveIntegerField()

    __error_code__ = 'CONFIG_NOT_FOUND'


class ConfigLog(ADCMModel):
    obj_ref = models.ForeignKey(ObjectConfig, on_delete=models.CASCADE)
    config = JSONField(default={})
    attr = JSONField(default={})
    date = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)

    __error_code__ = 'CONFIG_NOT_FOUND'


class ADCM(ADCMModel):
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=16, choices=(('ADCM', 'ADCM'),), unique=True)
    config = models.OneToOneField(ObjectConfig, on_delete=models.CASCADE, null=True)
    state = models.CharField(max_length=64, default='created')
    stack = JSONField(default=[])
    issue = JSONField(default={})

    @property
    def bundle_id(self):
        return self.prototype.bundle_id


class Cluster(ADCMModel):
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    config = models.OneToOneField(ObjectConfig, on_delete=models.CASCADE, null=True)
    state = models.CharField(max_length=64, default='created')
    stack = JSONField(default=[])
    issue = JSONField(default={})

    __error_code__ = 'CLUSTER_NOT_FOUND'

    @property
    def bundle_id(self):
        return self.prototype.bundle_id

    @property
    def edition(self):
        return self.prototype.bundle.edition

    @property
    def license(self):
        return self.prototype.bundle.license

    def __str__(self):
        return f'{self.name} ({self.id})'


class HostProvider(ADCMModel):
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    config = models.OneToOneField(ObjectConfig, on_delete=models.CASCADE, null=True)
    state = models.CharField(max_length=64, default='created')
    stack = JSONField(default=[])
    issue = JSONField(default={})

    __error_code__ = 'PROVIDER_NOT_FOUND'

    @property
    def bundle_id(self):
        return self.prototype.bundle_id

    @property
    def edition(self):
        return self.prototype.bundle.edition

    @property
    def license(self):
        return self.prototype.bundle.license

    def __str__(self):
        return str(self.name)


class Host(ADCMModel):
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    fqdn = models.CharField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    provider = models.ForeignKey(HostProvider, on_delete=models.CASCADE, null=True, default=None)
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, default=None)
    config = models.OneToOneField(ObjectConfig, on_delete=models.CASCADE, null=True)
    state = models.CharField(max_length=64, default='created')
    stack = JSONField(default=[])
    issue = JSONField(default={})

    __error_code__ = 'HOST_NOT_FOUND'

    @property
    def bundle_id(self):
        return self.prototype.bundle_id

    @property
    def monitoring(self):
        return self.prototype.monitoring

    def __str__(self):
        return "{}".format(self.fqdn)


class ClusterObject(ADCMModel):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    service = models.ForeignKey("self", on_delete=models.CASCADE, null=True, default=None)
    config = models.OneToOneField(ObjectConfig, on_delete=models.CASCADE, null=True)
    state = models.CharField(max_length=64, default='created')
    stack = JSONField(default=[])
    issue = JSONField(default={})

    __error_code__ = 'CLUSTER_SERVICE_NOT_FOUND'

    @property
    def bundle_id(self):
        return self.prototype.bundle_id

    @property
    def version(self):
        return self.prototype.version

    @property
    def name(self):
        return self.prototype.name

    @property
    def display_name(self):
        return self.prototype.display_name

    @property
    def description(self):
        return self.prototype.description

    @property
    def monitoring(self):
        return self.prototype.monitoring

    class Meta:
        unique_together = (('cluster', 'prototype'),)


class ServiceComponent(ADCMModel):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    service = models.ForeignKey(ClusterObject, on_delete=models.CASCADE)
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE, null=True, default=None)
    config = models.OneToOneField(ObjectConfig, on_delete=models.CASCADE, null=True)
    state = models.CharField(max_length=64, default='created')
    stack = JSONField(default=[])
    issue = JSONField(default={})

    __error_code__ = 'COMPONENT_NOT_FOUND'

    @property
    def name(self):
        return self.prototype.name

    @property
    def display_name(self):
        return self.prototype.display_name

    @property
    def description(self):
        return self.prototype.description

    @property
    def constraint(self):
        return self.prototype.constraint

    @property
    def requires(self):
        return self.prototype.requires

    @property
    def bound_to(self):
        return self.prototype.bound_to

    @property
    def monitoring(self):
        return self.prototype.monitoring

    class Meta:
        unique_together = (('cluster', 'service', 'prototype'),)


ACTION_TYPE = (
    ('task', 'task'),
    ('job', 'job'),
)

SCRIPT_TYPE = (
    ('ansible', 'ansible'),
    ('task_generator', 'task_generator'),
)


class Action(ADCMModel):
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    display_name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    ui_options = JSONField(default={})

    type = models.CharField(max_length=16, choices=ACTION_TYPE)
    button = models.CharField(max_length=64, default=None, null=True)

    script = models.CharField(max_length=160)
    script_type = models.CharField(max_length=16, choices=SCRIPT_TYPE)

    state_on_success = models.CharField(max_length=64, blank=True)
    state_on_fail = models.CharField(max_length=64, blank=True)
    state_available = JSONField(default=[])

    params = JSONField(default={})
    log_files = JSONField(default=[])

    hostcomponentmap = JSONField(default=[])
    allow_to_terminate = models.BooleanField(default=False)
    partial_execution = models.BooleanField(default=False)
    host_action = models.BooleanField(default=False)

    __error_code__ = 'ACTION_NOT_FOUND'

    def __str__(self):
        return "{} {}".format(self.prototype, self.name)

    class Meta:
        unique_together = (('prototype', 'name'),)


class SubAction(ADCMModel):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    display_name = models.CharField(max_length=160, blank=True)
    script = models.CharField(max_length=160)
    script_type = models.CharField(max_length=16, choices=SCRIPT_TYPE)
    state_on_fail = models.CharField(max_length=64, blank=True)
    params = JSONField(default={})


class HostComponent(ADCMModel):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    service = models.ForeignKey(ClusterObject, on_delete=models.CASCADE)
    component = models.ForeignKey(ServiceComponent, on_delete=models.CASCADE)
    state = models.CharField(max_length=64, default='created')

    class Meta:
        unique_together = (('host', 'service', 'component'),)


CONFIG_FIELD_TYPE = (
    ('string', 'string'),
    ('text', 'text'),
    ('password', 'password'),
    ('secrettext', 'secrettext'),
    ('json', 'json'),
    ('integer', 'integer'),
    ('float', 'float'),
    ('option', 'option'),
    ('variant', 'variant'),
    ('boolean', 'boolean'),
    ('file', 'file'),
    ('list', 'list'),
    ('map', 'map'),
    ('structure', 'structure'),
    ('group', 'group'),
)


class PrototypeConfig(ADCMModel):
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE, null=True, default=None)
    name = models.CharField(max_length=160)
    subname = models.CharField(max_length=160, blank=True)
    default = models.TextField(blank=True)
    type = models.CharField(max_length=16, choices=CONFIG_FIELD_TYPE)
    display_name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    limits = JSONField(default={})
    ui_options = JSONField(blank=True, default={})
    required = models.BooleanField(default=True)

    class Meta:
        unique_together = (('prototype', 'action', 'name', 'subname'),)


class PrototypeExport(ADCMModel):
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)

    class Meta:
        unique_together = (('prototype', 'name'),)


class PrototypeImport(ADCMModel):
    prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    min_version = models.CharField(max_length=80)
    max_version = models.CharField(max_length=80)
    min_strict = models.BooleanField(default=False)
    max_strict = models.BooleanField(default=False)
    default = JSONField(null=True, default=None)
    required = models.BooleanField(default=False)
    multibind = models.BooleanField(default=False)

    class Meta:
        unique_together = (('prototype', 'name'),)


class ClusterBind(ADCMModel):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    service = models.ForeignKey(ClusterObject, on_delete=models.CASCADE, null=True, default=None)
    source_cluster = models.ForeignKey(
        Cluster, related_name='source_cluster', on_delete=models.CASCADE
    )
    source_service = models.ForeignKey(
        ClusterObject,
        related_name='source_service',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )

    class Meta:
        unique_together = (('cluster', 'service', 'source_cluster', 'source_service'),)


JOB_STATUS = (
    ('created', 'created'),
    ('running', 'running'),
    ('success', 'success'),
    ('failed', 'failed')
)


class UserProfile(ADCMModel):
    login = models.CharField(max_length=32, unique=True)
    profile = JSONField(default='')


class Role(ADCMModel):
    name = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    user = models.ManyToManyField(User, blank=True)
    group = models.ManyToManyField(Group, blank=True)


class JobLog(ADCMModel):
    task_id = models.PositiveIntegerField(default=0)
    action_id = models.PositiveIntegerField()
    sub_action_id = models.PositiveIntegerField(default=0)
    pid = models.PositiveIntegerField(blank=True, default=0)
    selector = JSONField(default={})
    log_files = JSONField(default=[])
    status = models.CharField(max_length=16, choices=JOB_STATUS)
    start_date = models.DateTimeField()
    finish_date = models.DateTimeField(db_index=True)

    __error_code__ = 'JOB_NOT_FOUND'


class TaskLog(ADCMModel):
    action_id = models.PositiveIntegerField()
    object_id = models.PositiveIntegerField()
    pid = models.PositiveIntegerField(blank=True, default=0)
    selector = JSONField(default={})
    status = models.CharField(max_length=16, choices=JOB_STATUS)
    config = JSONField(null=True, default=None)
    attr = JSONField(default={})
    hostcomponentmap = JSONField(null=True, default=None)
    hosts = JSONField(null=True, default=None)
    verbose = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    finish_date = models.DateTimeField()


class GroupCheckLog(ADCMModel):
    job_id = models.PositiveIntegerField(default=0)
    title = models.TextField()
    message = models.TextField(blank=True, null=True)
    result = models.BooleanField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['job_id', 'title'], name='unique_group_job')
        ]


class CheckLog(ADCMModel):
    group = models.ForeignKey(GroupCheckLog, blank=True, null=True, on_delete=models.CASCADE)
    job_id = models.PositiveIntegerField(default=0)
    title = models.TextField()
    message = models.TextField()
    result = models.BooleanField()


LOG_TYPE = (
    ('stdout', 'stdout'),
    ('stderr', 'stderr'),
    ('check', 'check'),
    ('custom', 'custom'),
)

FORMAT_TYPE = (
    ('txt', 'txt'),
    ('json', 'json'),
)


class LogStorage(ADCMModel):
    job = models.ForeignKey(JobLog, on_delete=models.CASCADE)
    name = models.TextField(default='')
    body = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=16, choices=LOG_TYPE)
    format = models.CharField(max_length=16, choices=FORMAT_TYPE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['job'], condition=models.Q(type='check'), name='unique_check_job')
        ]


# Stage: Temporary tables to load bundle

class StagePrototype(ADCMModel):
    type = models.CharField(max_length=16, choices=PROTO_TYPE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, default=None)
    name = models.CharField(max_length=160)
    path = models.CharField(max_length=160, default='')
    display_name = models.CharField(max_length=160, blank=True)
    version = models.CharField(max_length=80)
    edition = models.CharField(max_length=80, default='community')
    license_path = models.CharField(max_length=160, default=None, null=True)
    license_hash = models.CharField(max_length=64, default=None, null=True)
    required = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    constraint = JSONField(default=[0, '+'])
    requires = JSONField(default=[])
    bound_to = JSONField(default={})
    adcm_min_version = models.CharField(max_length=80, default=None, null=True)
    description = models.TextField(blank=True)
    monitoring = models.CharField(max_length=16, choices=MONITORING_TYPE, default='active')

    __error_code__ = 'PROTOTYPE_NOT_FOUND'

    def __str__(self):
        return str(self.name)

    class Meta:
        unique_together = (('type', 'parent', 'name', 'version'),)


class StageUpgrade(ADCMModel):
    name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    min_version = models.CharField(max_length=80)
    max_version = models.CharField(max_length=80)
    min_strict = models.BooleanField(default=False)
    max_strict = models.BooleanField(default=False)
    from_edition = JSONField(default=['community'])
    state_available = JSONField(default=[])
    state_on_success = models.CharField(max_length=64, blank=True)


class StageAction(ADCMModel):
    prototype = models.ForeignKey(StagePrototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    display_name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    ui_options = JSONField(default={})

    type = models.CharField(max_length=16, choices=ACTION_TYPE)
    button = models.CharField(max_length=64, default=None, null=True)

    script = models.CharField(max_length=160)
    script_type = models.CharField(max_length=16, choices=SCRIPT_TYPE)

    state_on_success = models.CharField(max_length=64, blank=True)
    state_on_fail = models.CharField(max_length=64, blank=True)
    state_available = JSONField(default=[])

    params = JSONField(default={})
    log_files = JSONField(default=[])

    hostcomponentmap = JSONField(default=[])
    allow_to_terminate = models.BooleanField(default=False)
    partial_execution = models.BooleanField(default=False)
    host_action = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.prototype, self.name)

    class Meta:
        unique_together = (('prototype', 'name'),)


class StageSubAction(ADCMModel):
    action = models.ForeignKey(StageAction, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    display_name = models.CharField(max_length=160, blank=True)
    script = models.CharField(max_length=160)
    script_type = models.CharField(max_length=16, choices=SCRIPT_TYPE)
    state_on_fail = models.CharField(max_length=64, blank=True)
    params = JSONField(default={})


class StagePrototypeConfig(ADCMModel):
    prototype = models.ForeignKey(StagePrototype, on_delete=models.CASCADE)
    action = models.ForeignKey(StageAction, on_delete=models.CASCADE, null=True, default=None)
    name = models.CharField(max_length=160)
    subname = models.CharField(max_length=160, blank=True)
    default = models.TextField(blank=True)
    type = models.CharField(max_length=16, choices=CONFIG_FIELD_TYPE)
    display_name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    limits = JSONField(default={})
    ui_options = JSONField(blank=True, default={})   # JSON
    required = models.BooleanField(default=True)

    class Meta:
        unique_together = (('prototype', 'action', 'name', 'subname'),)


class StagePrototypeExport(ADCMModel):
    prototype = models.ForeignKey(StagePrototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)

    class Meta:
        unique_together = (('prototype', 'name'),)


class StagePrototypeImport(ADCMModel):
    prototype = models.ForeignKey(StagePrototype, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    min_version = models.CharField(max_length=80)
    max_version = models.CharField(max_length=80)
    min_strict = models.BooleanField(default=False)
    max_strict = models.BooleanField(default=False)
    default = JSONField(null=True, default=None)
    required = models.BooleanField(default=False)
    multibind = models.BooleanField(default=False)

    class Meta:
        unique_together = (('prototype', 'name'),)


class DummyData(ADCMModel):
    date = models.DateTimeField(auto_now=True)
