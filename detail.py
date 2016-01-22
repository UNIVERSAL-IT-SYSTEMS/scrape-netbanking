#!/usr/bin/env python
# coding: utf-8


class Detail:
    def __init__(self, _date, payment, withdrawal, transaction, balance):
        self._date = _date
        self._payment = payment
        self._withdrawal = withdrawal
        self._transaction = transaction
        self._balance = balance

    def __str__(self):
        return '{}: {}円, {}'.format(self._date.strftime('%Y-%m-%d'),
                                   self._payment if self._payment > 0 else self._withdrawal,
                                   self._transaction)

    def __repr__(self):
        return '{}: {}円, {}'.format(self._date.strftime('%Y-%m-%d'),
                                   self._payment if self._payment > 0 else self._withdrawal,
                                   self._transaction)

    @property
    def date(self):
        return self._date

    @property
    def payment(self):
        return self._payment

    @property
    def withdrawal(self):
        return self._withdrawal

    @property
    def transaction(self):
        return self._transaction

    @property
    def balance(self):
        return self._balance
