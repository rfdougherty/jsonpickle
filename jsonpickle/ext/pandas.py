from __future__ import absolute_import

import pandas as pd
from io import StringIO

from ..handlers import BaseHandler, register, unregister

__all__ = ['register_handlers', 'unregister_handlers']


class PandasDfHandler(BaseHandler):

    def flatten(self, obj, data):
        data['DataFrame'] = obj.to_csv(index=False)
        return data

    def restore(self, data):
        return pd.read_csv(StringIO(data['DataFrame']))

class PandasSeriesHandler(BaseHandler):

    def flatten(self, obj, data):
        data['Series'] = obj.to_csv()
        return data

    def restore(self, data):
        return pd.read_csv(StringIO(data['Series']), squeeze=True)


def register_handlers():
    register(pd.DataFrame, PandasDfHandler, base=True)
    register(pd.Series, PandasSeriesHandler, base=True)


def unregister_handlers():
    unregister(pd.DataFrame)
    unregister(pd.Series)
