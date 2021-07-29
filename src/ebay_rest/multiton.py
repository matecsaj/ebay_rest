# Standard library imports
import datetime
import threading


# Local imports
from .error import Error


class Multiton(object):
    """
    When init parameters match, reuse an old initialized object instead of making a new one.
    Objects that have not be been reused for an hour will be dropped from the pool.

    Use this when the cost of object creation is high or there is a big benefit to object sharing.

    Don't use this on data storage classes.

    In ebay_rest, Multiton helps avoid making redundant REST calls to eBay.
    Redundant calls waste time, erode daily call limits and can trigger an "Internal Server Error" at eBay.
    I suspect the latter is eBay protecting itself from customer code stuck in an endless loop.

    Multiton is a class decorator, and here is an example of how to use it.

    @Multiton
    class YourClass:
        pass

    Debugging tip, temporarily comment out the decorator is if object reuse is confusing diagnosis.

    To learn about the Multiton Creation (Anti)Pattern, visit https://en.wikipedia.org/wiki/Multiton_pattern.
    """
    def __init__(self, cls):
        self.__dict__.update({'instances': list(), 'lock': threading.Lock(), 'cls': cls})
        # The above accomplishes the following, without triggering a Pycharm warning and endless recursion.
        # self.instances = list()
        # self.lock = threading.Lock()
        # self.cls = cls

    def __call__(self, *args, **kwargs):
        with self.lock:
            # make a key with the parameters
            key = (args, kwargs)

            # search for a matching old instance
            for instance in self.instances:
                if instance['key'] == key:
                    break

            else:   # if not found then create a new instance
                try:
                    instance = {'key': key, 'object': self.cls(*args, **kwargs)}
                except Error:
                    raise
                self.instances.append(instance)

            return_object = instance['object']

            # record when we are touching the instance
            d_t = datetime.datetime.now()
            instance['touched'] = d_t

            # delete any instances that have not been touched for a while
            # don't panic, if the instance's object is still in use, it will not be garbage collected
            d_t -= datetime.timedelta(hours=1.0)
            to_delete = list()
            for index, instance in enumerate(self.instances):
                if instance['touched'] < d_t:
                    to_delete.append(index)
            for index in reversed(to_delete):
                del self.instances[index]

            return return_object

    def __getattr__(self, attr):
        return getattr(self.cls, attr)

    def __setattr__(self, attr, value):
        setattr(self.cls, attr, value)

    def __instancecheck__(self, other):
        return isinstance(other, self.cls)
