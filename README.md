# Scrape Netbanking

ネットバンキングをスクレイピングして入出金明細を取得します。
WebDriverにChromeを使用します

* 三菱東京UFJ銀行
* 住信SBIネット銀行

## 使い方

[ChromeDriver - WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads)からDriverをカレントディレクトリにダウンロード

```sh
$ pip install -r requirements.txt

$ export MUFG_ID={Your id}
$ export MUFG_PASSWORD={Your passowrd}

$ export SBI_ID={Your id}
$ export SBI_PASSWORD={Your passowrd}

$ ./example.py
```