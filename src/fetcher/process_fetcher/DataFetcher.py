from typing import Protocol

from src.fetcher.FetcherInterface import FetcherInterface
from src.model.Model import Model


class DataFetcher(Protocol, FetcherInterface):

    def __init__(self, model: Model):
        self.model = model
