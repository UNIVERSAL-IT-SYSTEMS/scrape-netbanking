#!/usr/bin/env python
# coding: utf-8

import datetime
import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

MUFG_TOP_URL = 'https://entry11.bk.mufg.jp/ibg/dfw/APLIN/loginib/login?_TRANID=AA000_001'
INFORMATION_TITLE = 'お知らせ - 三菱東京ＵＦＪ銀行'

driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')


def login(account_id: str, ib_password: str):
    driver.get(MUFG_TOP_URL)
    driver.find_element_by_id('account_id').send_keys(account_id)
    driver.find_element_by_id('ib_password').send_keys(ib_password)
    driver.find_element_by_xpath('//img[@alt="ログイン"]').click()


def logout():
    driver.find_element_by_link_text('ログアウト').click()


def read_information():
    """
    お知らせがある場合は既読にします
    :return:
    """
    while True:
        if not driver.title == INFORMATION_TITLE:
            return
        information = driver.find_element_by_xpath(
                '//table[@class="data"]/tbody/tr')
        information.find_element_by_name('hyouzi').click()
        driver.find_element_by_xpath('//img[@alt="トップページへ"]').click()


def select_selectbox_value(element_name: str, value: str):
    """
    セレクトボックスの値を選択します

    :param element_name:
    :param value:
    :return:
    """
    selectbox = Select(driver.find_element_by_name(element_name))
    selectbox.select_by_visible_text(str(value))


def select_time_period(_from: datetime, _to: datetime):
    """
    指定した表示期間を選択します

    :param _from:
    :param _to:
    :return:
    """

    driver.find_element_by_name('SHOUKAIKIKAN_RADIO').click()

    select_selectbox_value('SHOUKAIKIKAN_FROM_Y', str(_from.year))
    select_selectbox_value('SHOUKAIKIKAN_FROM_M', str(_from.month))
    select_selectbox_value('SHOUKAIKIKAN_FROM_D', str(_from.day))
    select_selectbox_value('SHOUKAIKIKAN_TO_Y', str(_to.year))
    select_selectbox_value('SHOUKAIKIKAN_TO_M', str(_to.month))
    select_selectbox_value('SHOUKAIKIKAN_TO_D', str(_to.day))


def show_details():
    banking_list = driver.find_elements_by_xpath(
            '//table[@class="data yen_nyushutsukin_001"]/tbody/tr')

    for banking in banking_list:
        detail = banking.find_elements_by_tag_name('td')

        date = datetime.datetime.strptime(detail[0].text.replace('\n', ''), '%Y年%m月%d日')

        payment = in_or_out_payment(detail[1].text, detail[2].text)
        # total = to_number(detail[4].text)

        print('{}: {}'.format(date, payment))

    try:
        driver.find_element_by_xpath('//a/img[@alt="新しい明細"]').click()
    except NoSuchElementException:
        return
    else:
        # 例外がない(=次のページがある)から次のページへ
        show_details()


def to_number(yen: str) -> int:
    """
    xxx,xxx,xxx円からカンマと「円」を削除します

    :param yen:
    :return: int:
    """
    if yen == '':
        return 0
    return int(yen.replace(',', '').replace('円', ''))


def in_or_out_payment(_out: str, _in: str) -> int:
    """
    入出金の判定を行います

    :param _out:
    :param _in:
    :return:
    """
    if not _out == '':
        # 出金
        return to_number(_out) * -1
    # 入金
    return to_number(_in)


def main(_from: datetime, _to: datetime):
    try:
        account_id = os.environ['ACCOUNT_ID']
        ib_password = os.environ['IB_PASSWORD']

        login(account_id, ib_password)

        # お知らせ画面がある場合は既読にする
        read_information()

        # 残高を取得
        total = driver.find_element_by_id('setAmountDisplay')
        total_amount = to_number(total.text)

        print('{:,d}円'.format(total_amount))

        driver.find_element_by_xpath('//img[@alt="入出金明細をみる"]').click()

        # 期間を指定する
        select_time_period(_from, _to)
        driver.find_element_by_xpath('//img[@alt="照会"]').click()

        show_details()

        logout()
    finally:
        driver.close()

if __name__ == '__main__':
    start = datetime.datetime(year=2014, month=1, day=1)
    end = datetime.datetime.now()
    main(start, end)


