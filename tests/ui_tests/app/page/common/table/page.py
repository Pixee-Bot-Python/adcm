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
from contextlib import contextmanager

import allure
from adcm_pytest_plugin.utils import wait_until_step_succeeds
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.remote.webelement import WebElement

from tests.ui_tests.app.page.common.base_page import BasePageObject
from tests.ui_tests.app.page.common.table.locator import CommonTable
from tests.ui_tests.app.page.common.tooltip_links.locator import CommonToolbarLocators


class CommonTableObj(BasePageObject):
    """Class for manipulating with common tables elements."""

    LOADING_STATE_TEXT = 'autorenew'

    def __init__(self, driver, base_url, table_class_locators=CommonTable):
        super().__init__(driver, base_url)
        self.table = table_class_locators

    @property
    def row_count(self) -> int:
        """Get amount of rows on page"""
        return len(self.get_all_rows())

    @allure.step("Get all rows from the table")
    def get_all_rows(self) -> list:
        try:
            return self.find_elements(self.table.row, timeout=5)
        except TimeoutException:
            return []

    def get_row(self, row_num: int = 0) -> WebElement:
        """Get exactly one row"""

        def table_has_enough_rows():
            current_row_count = self.row_count
            assert (
                row_num + 1 <= current_row_count
            ), f"Table has only {current_row_count} rows when row #{row_num} was requested"

        wait_until_step_succeeds(table_has_enough_rows, timeout=5, period=0.1)
        rows = self.get_all_rows()
        return rows[row_num]

    def click_previous_page(self):
        self.find_and_click(self.table.Pagination.previous_page)

    def click_next_page(self):
        self.find_and_click(self.table.Pagination.next_page)

    @contextmanager
    def wait_rows_change(self):
        """Wait changing rows amount."""

        current_amount = len(self.get_all_rows())
        yield

        def wait_scroll():
            assert (
                len(self.get_all_rows()) != current_amount
            ), "Amount of rows on the page hasn't changed"

        self.wait_element_hide(CommonToolbarLocators.progress_bar)
        wait_until_step_succeeds(wait_scroll, period=1, timeout=10)

    @allure.step("Click on page number {number}")
    def click_page_by_number(self, number: int):
        page_loc = self.table.Pagination.page_to_choose_btn
        WDW(self.driver, self.default_loc_timeout).until(
            EC.presence_of_element_located([page_loc.by, page_loc.value.format(number)]),
            message=f"Can't find page {number} in table on page {self.driver.current_url} "
            f"for {self.default_loc_timeout} seconds",
        ).click()

    @allure.step("Check pagination")
    def check_pagination(self, second_page_item_amount: int):
        params = {"fist_page_cluster_amount": 10}
        self.wait_element_hide(CommonToolbarLocators.progress_bar, timeout=30)
        with self.wait_rows_change():
            self.click_page_by_number(2)
        assert (
            self.row_count == second_page_item_amount
        ), f"Second page should contains {second_page_item_amount} items"
        with self.wait_rows_change():
            self.click_page_by_number(1)
        assert (
            self.row_count == params["fist_page_cluster_amount"]
        ), f"First page should contains {params['fist_page_cluster_amount']} items"
        with self.wait_rows_change():
            self.click_next_page()
        assert (
            self.row_count == second_page_item_amount
        ), f"Next page should contains {second_page_item_amount} items"
        with self.wait_rows_change():
            self.click_previous_page()
        assert (
            self.row_count == params["fist_page_cluster_amount"]
        ), f"Previous page should contains {params['fist_page_cluster_amount']} items"