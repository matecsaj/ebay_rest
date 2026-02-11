# Standard library imports
import datetime
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

# Local imports


class Multiton(type):
    """
    When init parameters match, reuse an old initialized object instead of making a new one.
    Objects that have not been reused for an hour will be dropped from the pool.

    Use this when the cost of object creation or maintenance is high.

    Don't use this with any class that has public setter methods (methods that modify their instance state
    after __init__). Since Multiton returns the same object for identical initialization parameters,
    any later mutations would create unexpected state for other callers. Classes should be immutable
    after construction is complete or only use private methods with internal locking for state changes.

    Thread-safe: Uses a reentrant lock to prevent race conditions when creating or accessing instances.
    The reentrant lock allows nested instantiation (a Multiton class creating another Multiton class
    in its __init__) without causing deadlock.

    In ebay_rest, Multiton helps avoid making redundant REST calls to eBay.
    Redundant calls waste time, erode daily call limits, and can trigger an "Internal Server Error" at eBay.
    I suspect the latter is eBay protecting itself from customer code stuck in an endless loop.

    Multiton is a metaclass, and here is an example of how to use it.

    class YourClass(metaclass=Multiton):
        pass

    Debugging tips:
    1. Temporarily remove "metaclass=Multiton" from a class if object reuse is causing confusion.
    2. Temporarily uncomment the line after `def __call__' to globally disable multiton behavior.

    To learn about the Multiton Creation (Anti)Pattern, visit https://en.wikipedia.org/wiki/Multiton_pattern.
    """

    _instances: List[Dict[str, Any]] = []
    _lock: RLock = RLock()

    def __call__(cls: type, *args: Any, **kwargs: Any) -> Any:
        # return super().__call__(*args, **kwargs)  # uncomment to globally disable multiton behavior

        with Multiton._lock:
            return_object: Optional[Any] = None
            d_t: datetime.datetime = datetime.datetime.now()
            key: Tuple[type, Tuple[Any, ...], Dict[str, Any]] = (
                cls,
                args,
                kwargs,
            )  # form a key with the class object and all the parameters

            # search for a matching old instance
            for instance in Multiton._instances:
                if instance["key"] == key:
                    instance["touched"] = d_t
                    return_object = instance["object"]
                    break

            # if not found, then create a new instance
            if return_object is None:
                return_object = super().__call__(*args, **kwargs)
                Multiton._instances.append(
                    {"key": key, "object": return_object, "touched": d_t}
                )

            # delete any instances that have not been touched for a while
            # don't panic, if the instance's object is still in use, it will not be garbage collected
            d_t -= datetime.timedelta(hours=1.0)
            to_delete: List[int] = list()
            for index, instance in enumerate(Multiton._instances):
                if instance["touched"] < d_t:
                    to_delete.append(index)
            for index in reversed(to_delete):
                del Multiton._instances[index]

            return return_object
