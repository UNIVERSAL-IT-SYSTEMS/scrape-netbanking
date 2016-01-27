#!/usr/bin/env python
# coding: utf-8

import datetime
import os

from mongoengine import Document
from mongoengine import connect
from mongoengine import fields
from selenium import webdriver
from selenium.webdriver.support.ui import Select

MUFG_TOP_URL = 'https://entry11.bk.mufg.jp/ibg/dfw/APLIN/loginib/login?_TRANID=AA000_001'
INFORMATION_TITLE = 'お知らせ - 三菱東京ＵＦＪ銀行'

driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')

account_id = os.environ['ACCOUNT_ID']
ib_password = os.environ['IB_PASSWORD']

connect('moneylog')


class MoneyLog(Document):
    date = fields.DateTimeField()
    payment = fields.IntField()
    remark = fields.StringField()
    total = fields.IntField()

    def __str__(self):
        return '{}: {}: {}'.format(self.date, self.payment, self.remark)


def login():
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


def show_details(_from: datetime, _to: datetime):
    """
    指定した期間の明細一覧画面を表示します

    :param _from:
    :param _to:
    :return:
    """

    driver.find_element_by_xpath('//img[@alt="入出金明細をみる"]').click()

    driver.find_element_by_name('SHOUKAIKIKAN_RADIO').click()

    select_selectbox_value('SHOUKAIKIKAN_FROM_Y', str(_from.year))
    select_selectbox_value('SHOUKAIKIKAN_FROM_M', str(_from.month))
    select_selectbox_value('SHOUKAIKIKAN_FROM_D', str(_from.day))
    select_selectbox_value('SHOUKAIKIKAN_TO_Y', str(_to.year))
    select_selectbox_value('SHOUKAIKIKAN_TO_M', str(_to.month))
    select_selectbox_value('SHOUKAIKIKAN_TO_D', str(_to.day))

    driver.find_element_by_xpath('//img[@alt="照会"]').click()


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
        login()

        # お知らせ画面がある場合は既読にする
        read_information()

        # 残高を取得
        total = driver.find_element_by_id('setAmountDisplay')
        total_amount = to_number(total.text)

        print('{:,d}円'.format(total_amount))

        # 入出金明細画面に移動
        show_details(_from, _to)

        # TODO 複数ページ対応

        banking_list = driver.find_elements_by_xpath(
                '//table[@class="data yen_nyushutsukin_001"]/tbody/tr')

        for banking in banking_list:
            detail = banking.find_elements_by_tag_name('td')

            date = datetime.datetime.strptime(detail[0].text.replace('\n', ''), '%Y年%m月%d日')

            payment = in_or_out_payment(detail[1].text, detail[2].text)
            total = to_number(detail[4].text)

            m = MoneyLog(date=date, payment=payment, remark=detail[3].text,
                         total=total)
            m.save()
            print(m)

        logout()
    finally:
        driver.close()

if __name__ == '__main__':
    today = datetime.datetime.now()
    main(today, today)


