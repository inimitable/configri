#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""""
from abc import abstractmethod


class ConfigBackendBase:
    def __init__(self, source):
        self.source = source

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def load_or_create(self, data):
        pass

    @abstractmethod
    def set_source(self, source):
        pass

    @abstractmethod
    def create(self, data):
        pass
