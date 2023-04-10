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

from cm.models import Prototype
from rest_framework.serializers import CharField, IntegerField, SerializerMethodField

from adcm.serializers import EmptySerializer


class PrototypeVersionSerializer(EmptySerializer):
    prototype_id = IntegerField(source="pk")
    version = CharField()


class PrototypeUISerializer(EmptySerializer):
    display_name = CharField()
    versions = SerializerMethodField()

    @staticmethod
    def get_versions(obj: Prototype) -> str | None:
        queryset = Prototype.objects.filter(type=obj.type, display_name=obj.display_name).order_by("-version")
        serializer = PrototypeVersionSerializer(instance=queryset, many=True)

        return serializer.data