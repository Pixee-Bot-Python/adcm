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


class CommonTable:
    header = Locator(By.XPATH, "//mat-header-cell/div", "Table header")
    row = Locator(By.XPATH, "//mat-row", "Table row")

    class Pagination:
        previous_page = Locator(By.XPATH, "//button[@aria-label='Previous page']", "Previous page button")
        first_page = Locator(By.XPATH, "//div[@class='mat-paginator-range-actions']//a[text()='1']",
                             "First page button")
        second_page = Locator(By.XPATH, "//div[@class='mat-paginator-range-actions']//a[text()='2']",
                              "Second page button")
        next_page = Locator(By.XPATH, "//button[@aria-label='Next page']", "Next page button")
