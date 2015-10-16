#!/usr/bin/env python
# coding: utf-8

import os
import time
import datetime
from selenium import webdriver
from models import Statement


class Sbi:
    """
    住信SBIの入出金明細の照会結果画面をスクレイピングして
    入出金一覧を取得します
    """

    _LOGIN_URL = 'https://www.netbk.co.jp/wpl/NBGate'

    WAIT_SEC = 3

    def __init__(self, _id, _password):
        assert _id, 'ID is None'
        assert _password, 'password is None'
        self._id = _id
        self._password = _password
        self._browser = None
        self._statement_dict = {}

    def scrape(self):
        self._browser = webdriver.PhantomJS()
        try:
            self._login()
            self._skip_information()
            self._get_statements()
            self._logout()
        finally:
            self._browser.quit()

    def get(self, _date=None):
        if _date is None:
            return self._statement_dict
        return self._statement_dict.get(_date, [])

    @property
    def today(self):
        key = datetime.datetime.now().strftime('%Y%m%d')
        return self.get(key)

    @property
    def yesterday(self):
        key = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        return self.get(key)

    def _login(self):
        self._browser.get(self._LOGIN_URL)
        time.sleep(self.WAIT_SEC)
        self._browser.find_element_by_name('userName').send_keys(self._id)
        self._browser.find_element_by_name('loginPwdSet').send_keys(self._password)
        self._browser.find_element_by_xpath('//input[@alt="ログイン"]').click()
        time.sleep(self.WAIT_SEC)

    def _skip_information(self):
        """重要なお知らせ画面をスキップします
           SBIは既読必須ではないので未読のままスキップする"""
        if self._browser.current_url == 'https://www.netbk.co.jp/wpl/NBGate/i010101CT':
            self._browser.find_element_by_name('ACT_doNext').click()

    def _get_statements(self):
        """
        入出金の明細を取得します
        """

        # 入出金明細画面に移動
        self._browser.find_element_by_link_text('入出金明細').click()
        time.sleep(self.WAIT_SEC)

        # 明細一覧を取得
        banking_list = self._browser.find_elements_by_xpath(
            '//div[@class="tableb02"]/table/tbody/tr')

        statement_dict = {}

        for banking in banking_list:
            detail = banking.find_elements_by_tag_name('td')

            _date = datetime.datetime.strptime(detail[0].text.replace('\n', ''),
                                               '%Y/%m/%d')

            state = Statement(_date,
                              self._yen_to_int(detail[3].text),
                              self._yen_to_int(detail[3].text),
                              detail[1].text,
                              self._yen_to_int(detail[4].text))
            key = _date.strftime('%Y%m%d')

            if statement_dict.get(key) is None:
                statement_dict[key] = [state]
            else:
                t = statement_dict[key]
                t.append(state)

        self._statement_dict = statement_dict

    def _yen_to_int(self, yen):
        """カンマと「円」を削除します"""
        if yen == '':
            return 0
        return int(yen.replace(',', '').replace('円', ''))

    def _logout(self):
        self._browser.find_element_by_xpath('//img[@alt="ログアウト"]').click()
        time.sleep(self.WAIT_SEC)

if __name__ == '__main__':
    sbi = Sbi(os.environ.get('SBI_ID'),
              os.environ.get('SBI_PASSWORD'))
    sbi.scrape()

    print(sbi.yesterday)  # 前日の入出金を取得
    print(sbi.today)  # 当日の入出金を取得
    print(sbi.get('20150824'))  # 2015/8/24の入出金を取得
