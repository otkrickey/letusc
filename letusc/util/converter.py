def strs_converter(data: list) -> list[str]:
    if not (isinstance(data, list) and all(isinstance(item, str) for item in data)):
        raise ValueError
    return data


class SplitConverter:
    _cache = {}

    def __init__(self, code: str, length: int):
        split = code.split(":")
        if len(split) != length:
            raise ValueError
        self._cache.update({code: split})

    def get(self, code: str, index: int) -> str:
        return self._cache[code][index]

    def get_multi(self, code: str, *index: int) -> list[str]:
        return [self._cache[code][i] for i in index]

    def delete(self, code: str) -> None:
        del self._cache[code]


def get_split_converter(code: str, length: int):
    _class = SplitConverter(code, length)
    return _class.get, _class.get_multi, _class.delete
