# Standard library imports
import datetime

# Local imports
from .error import Error


class Multiton(type):
    """
    When init parameters match, reuse an old initialized object instead of making a new one.
    Objects that have not been reused for an hour will be dropped from the pool.

    Use this when the cost of object creation or maintenance is high.

    Don't use this with any class that, excepting __init__, has public setter methods.

    When using treading, the creation of duplicate instances is possible, you may want to use locking.

    In ebay_rest, Multiton helps avoid making redundant REST calls to eBay.
    Redundant calls waste time, erode daily call limits and can trigger an "Internal Server Error" at eBay.
    I suspect the latter is eBay protecting itself from customer code stuck in an endless loop.

    Multiton is a metaclass, and here is an example of how to use it.

    class YourClass(metaclass=Multiton):
        pass

    Debugging tip, temporarily remove "metaclass=Multiton" if object reuse is confusing diagnosis.

    To learn about the Multiton Creation (Anti)Pattern, visit https://en.wikipedia.org/wiki/Multiton_pattern.
    """
    _instances = list()

    # TODO Is it possible to improve the implementation with @functools.lru_cache()?
    def __call__(cls, *args, **kwargs):
        return_object = None
        d_t = datetime.datetime.now()
        key = (args, kwargs)    # form a key with all the parameters

        # search for a matching old instance
        for instance in Multiton._instances:
            if instance['key'] == key:
                instance['touched'] = d_t
                return_object = instance['object']
                break

        # if not found then create a new instance
        if return_object is None:
            try:
                return_object = super(Multiton, cls).__call__(*args, **kwargs)
            except Error:
                raise
            else:
                Multiton._instances.append({'key': key, 'object': return_object, 'touched': d_t})

        # delete any instances that have not been touched for a while
        # don't panic, if the instance's object is still in use, it will not be garbage collected
        d_t -= datetime.timedelta(hours=1.0)
        to_delete = list()
        for index, instance in enumerate(Multiton._instances):
            if instance['touched'] < d_t:
                to_delete.append(index)
        for index in reversed(to_delete):
            del Multiton._instances[index]

        return return_object
