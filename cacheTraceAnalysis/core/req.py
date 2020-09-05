
import inspect
import collections

try: 
  from dataclasses import dataclass

  @dataclass
  class Req:
    logical_time: int
    obj_id: int
    real_time: int = -1
    obj_size: int = -1
    req_size: int = -1
    key_size: int = -1
    value_size: int = -1
    req_range_start: int = -1
    req_range_end: int = -1
    cnt: int = 1
    op: str = ""
    ttl: int = -1
    other: str = ""

    def ss(self):
        print("locals {}".format(locals().items()))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        members = inspect.getmembers(self, lambda a: not(inspect.isroutine(a)))
        members = [a for a in members if not(
            a[0].startswith('__') and a[0].endswith('__'))]
        # print(members)

        s = f"Req("
        for member in members:
            if member[1] != -1 and member[1] != "":
                s += "{}={},\t".format(*member)
        s = s[:-1] + ")"
        return s


except:
  Req = collections.namedtuple('Req', ["logical_time", "obj_id", "real_time", "obj_size", "req_size", 
      "key_size", "value_size", "req_range_start", "req_range_end", "cnt", "op", "ttl", "client_id", "namespace"])
  # Req.__new__.__defaults__ = (None,) * len(Req._fields)
  Req.__new__.__defaults__ = (None, None, None, 1, 1, 0, 1, None, None, 1, None, None, None, None)







