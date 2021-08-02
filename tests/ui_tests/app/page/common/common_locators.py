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

from selenium.webdriver.common.by import By

from tests.ui_tests.app.helpers.locator import Locator


class CommonLocators:
    """Locators common to all pages"""

    socket = Locator(By.CLASS_NAME, "socket", "open socket marker")
    profile = Locator(By.CLASS_NAME, "profile", "profile load marker")
    load_marker = Locator(By.CLASS_NAME, 'load_complete', "page load marker")


class ObjectPageLocators:
    """Common locators for object's detailed page"""

    title = Locator(
        By.XPATH,
        "//mat-drawer-content/mat-card/mat-card-header/div/mat-card-title",
        "Title on object page",
    )
    subtitle = Locator(
        By.XPATH,
        "//mat-drawer-content/mat-card/mat-card-header/div/mat-card-subtitle",
        "Subtitle on object page",
    )
