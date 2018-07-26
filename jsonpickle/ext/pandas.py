from __future__ import absolute_import

import pandas as pd
from io import StringIO
import zlib

from ..handlers import BaseHandler, register, unregister
from ..util import b64decode, b64encode


__all__ = ['register_handlers', 'unregister_handlers']

class PandasProcessor():

    def __init__(self, size_threshold=500, compression=zlib):
        """
        :param size_threshold: nonnegative int or None
            valid values for 'size_threshold' are all nonnegative
            integers and None
            if size_threshold is None, dataframes are always stored as csv strings
        :param compression: a compression module or None
            valid values for 'compression' are {zlib, bz2, None}
            if compresion is None, no compression is applied
        """
        self.size_threshold = size_threshold
        self.compression = compression

    def flatten_pandas(self, buf, data):
        if self.size_threshold is not None and len(buf) > self.size_threshold:
            if self.compression:
                buf = self.compression.compress(buf.encode())
                data['comp'] = True
            data['values'] = b64encode(buf)
            data['txt'] = False
        else:
            data['values'] = buf
            data['txt'] = True
        return data

    def restore_pandas(self, data):
        if data.get('txt', True):
            # It's just csv-encoded text...
            csv = data['values']
        else:
            csv = b64decode(data['values'])
            if data.get('comp', False):
                csv = self.compression.decompress(csv).decode()
        return csv


class PandasDfHandler(BaseHandler):
    pp = PandasProcessor()

    def flatten(self, obj, data):
        data = self.pp.flatten_pandas(obj.to_csv(index=False), data)
        return data

    def restore(self, data):
        csv = self.pp.restore_pandas(data)
        return pd.read_csv(StringIO(csv))

class PandasSeriesHandler(BaseHandler):
    pp = PandasProcessor()

    def flatten(self, obj, data):
        data = self.pp.flatten_pandas(obj.to_csv(), data)
        return data

    def restore(self, data):
        csv = self.pp.restore_pandas(data)
        return pd.read_csv(StringIO(csv), squeeze=True)


def register_handlers():
    register(pd.DataFrame, PandasDfHandler, base=True)
    register(pd.Series, PandasSeriesHandler, base=True)


def unregister_handlers():
    unregister(pd.DataFrame)
    unregister(pd.Series)
