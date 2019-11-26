#!/bin/sh
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

# shellcheck disable=SC1091
source /etc/adcmenv

cleanupwaitstatus

sv_stop() {
    for s in nginx wsgi status cron; do
        /sbin/sv stop $s
    done
}

trap "sv_stop; exit" SIGTERM

trap '' SIGCHLD

runsvdir -P /etc/service &

while (true); do wait; done;
