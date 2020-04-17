import json
import logging
import sys
from typing import Text, Union, Any, Dict
import attr

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class GameError(Exception):
    pass


def _isprimitive(value: Any):
    if (isinstance(value, int) or
            isinstance(value, str) or isinstance(value, float) or isinstance(value, bool)):
        return True
    else:
        return False


class Serializable(object):

    def _to_dict_item(self, v):
        if _isprimitive(v):
            return v
        if isinstance(v, list):
            l = list()
            for item in v:
                l.append(self._to_dict_item(item))
            return l
        elif isinstance(v, Serializable):
            return v.to_dict()
        else:
            raise GameError(
                'Serializable object contains unsupported attribute {}={}'.format(k, v))

    def to_dict(self):
        log_message('to_dict called for {}'.format(self.__class__))
        d = {'class': self.__class__.__name__}
        for k, v in vars(self).items():
            d[k] = self._to_dict_item(v)
        return d

    @classmethod
    def from_dict(cls, json_dict: Dict):
        o = cls()
        for k, v in json_dict.items():
            if k == 'class':
                continue

            if k in attr.fields_dict(cls) and _isprimitive(v):
                setattr(o, k, v)
            else:
                raise GameError(
                    'Unable to instantiate type {} from dict {} with attribute {}={}'.format(str(cls), json_dict, k, v))
        return o

    def to_json(self):
        return json.dumps(self.to_dict())


def log_message(message):
    logging.info(message)
