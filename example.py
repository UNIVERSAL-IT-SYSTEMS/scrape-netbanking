#!/usr/bin/env python
# coding: utf-8

import os
from mufg import Mufg


def main():
    mufg = Mufg(os.environ.get('MUFG_ID'),
                os.environ.get('MUFG_PASSWORD'))
    mufg.scrape()

    print(mufg.yesterday)  # 前日の入出金を取得
    print(mufg.today)  # 当日の入出金を取得
    print(mufg.get('20150831'))  # 2015/8/31の入出金を取得

if __name__ == '__main__':
    main()