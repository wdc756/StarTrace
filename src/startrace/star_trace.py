# Imports
########################################################################################################################




# Class utils
from typing import Any, Literal
from abc import ABC, abstractmethod
from starshift import Shift, ShiftField, shift_validator, shift_repr, shift_serializer, shift_setter

# Used to get date and time for some vars
from datetime import datetime



# Classes
########################################################################################################################



# Helper Classes
############################################################

class Iter(Shift):
    """Iterates over a range of vals"""

    val: Any = None
    start: Any
    end: Any
    step: Any

    def __post_init__(self) -> None:
        # Automatically set val if not provided
        if self.val is None:
            self.val = self.start

        # Make sure whatever types val and step are, they can be added together
        try:
            _ = self.val + self.step
        except Exception as e:
            raise TypeError(f"Iter: could not increment val by step")

        # Make sure whatever types val, start, and end are they can be compared
        try:
            _ = self.val <= self.start
            _ = self.val <= self.end
            _ = self.val <= self.step
        except Exception as e:
            raise TypeError("Iter: could not compare val, start, end, or step")

        # If step is 0, we can't progress, so throw
        if self.step == 0:
            raise ValueError("Iter: step cannot be zero.")

        # If step +, val must be >= start and <= end
        if self.step > 0:
            if self.val < self.start:
                raise ValueError("Iter: val must be > start.")
            if self.val > self.end:
                raise ValueError("Iter: val must be < end.")
        # If step -, val must be <= start and >= end
        else:
            if self.val > self.start:
                raise ValueError("Iter: val must be < start.")
            if self.val < self.end:
                raise ValueError("Iter: val must be > end.")

        # If start > end and step > 0 the range is invalid, so throw
        if self.start > self.end and self.step > 0:
            raise ValueError("Iter: start must be < end when stepping up.")
        # If start < end and step < 0 the range is invalid, so throw
        if self.start < self.end and self.step < 0:
            raise ValueError("Iter: start must be > end when stepping down.")

    @shift_repr('val')
    def _repr_value(self, val) -> str | None:
        if val != self.start:
            return f"val={val}"
        return None

    @shift_serializer('val')
    def _serialize_value(self, val) -> dict[str, Any] | None:
        if val != self.start:
            return { 'val': val }
        return None



    def __len__(self) -> int | None:
        """Return the number of iterations left in the range"""
        return self.count_iterations()

    def __iter__(self) -> Iter:
        """Used to iterate over `for item in instance` syntax"""
        return self

    def __next__(self) -> Any:
        """Used by iterables to get the next val until StopIteration is raised"""
        if self.count_iterations() == 0:
            raise StopIteration
        val = self.val
        self.next()
        return val

    def count_iterations(self) -> int:
        """Return the number of iterations left in the range"""
        return (self.end - self.val) // self.step

    def next(self) -> bool:
        """Increments the current iterator val to the next and returns True if it had space to increment, False otherwise"""
        if self.step > 0:
            if self.val < self.end:
                self.val += self.step
                return True
            else:
                return False
        else:
            if self.val > self.end:
                self.val += self.step
                return True
            else:
                return False

    def last(self) -> bool:
        """Decrement the current token val to the last and returns True if it had space to decrement, False otherwise"""
        if self.step > 0:
            if self.val > self.start:
                self.val -= self.step
                return True
            else:
                return False
        else:
            if self.val < self.start:
                self.val -= self.step
                return True
            else:
                return False

    def reset(self) -> None:
        """Resets the val to the opposite bound"""
        if self.end <= self.val:
            self.val = self.start
        else:
            self.val = self.end

class Link(Shift):
    """A mutable object wrapper for LinkTokens"""

    val: Any
    args: list[Any] = []
    kwargs: dict[str, Any] = {}

    @shift_validator('val')
    def _validate_val(self, val: Any) -> bool:
        """Ensure the val is not a Link instance (avoid infinite circular references)"""
        if isinstance(val, Link):
            raise ValueError("Link: val cannot be another Link (circular reference)")
        return True

    def __post_init__(self) -> None:
        """Validate args and kwargs"""
        if not callable(self.val) and (len(self.args) > 0 or len(self.kwargs) > 0):
            raise ValueError('Link was created with args/kwargs but the value is not callable')



    def __call__(self) -> Any:
        if callable(self.val):
            return self.val(*self.args, **self.kwargs)
        return self.val



# Var Classes
############################################################

class Var(Shift, ABC):
    """An abstract interface for all vars to inherit"""

    type: str
    name: str



    def eval(self) -> str:
        """Evaluate this var"""
        return str(self)

    @abstractmethod
    def __str__(self) -> str:
        """Return the string evaluation of the Var"""
        pass

    def __len__(self) -> int:
        """Return the length of the val/vals in this instance"""
        return self.count_iterations()

    @abstractmethod
    def count_iterations(self) -> int:
        """Return the number of iterations left"""
        pass

    def __add__(self, other: int) -> bool:
        """Increment this instance by other and return whether this instance has more increments left"""
        for i in range(0, abs(other)):
            if other < 0:
                if not self.last():
                    return False
            else:
                if not self.next():
                    return False
        return True

    def __sub__(self, other) -> bool:
        """Decrement this instance by other and return whether this instance has more decrements left"""
        return self.__add__(-other)

    @abstractmethod
    def next(self) -> bool:
        """Increment this instance and return whether this instance has more increments left"""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset this instance"""
        pass

    @abstractmethod
    def last(self) -> bool:
        """Decrement this instance and return whether this instance has more decrements left"""
        pass

class ConstVar(Var):
    """A Var that holds a constant val"""

    type: str = ShiftField(eq="const")
    name: str = ShiftField(min_len=1)
    val: Any

    @shift_validator('val')
    def _validate_val(self, val) -> bool:
        try:
            _ = str(val)
            return True
        except TypeError:
            raise ValueError('ConstVar: could not convert val to str')



    def __str__(self) -> str:
        """Return the string evaluation of the ConstVar"""
        return str(self.val)

    def count_iterations(self) -> int:
        """Returns 0 because ConstVar never changes"""
        return 0

    def next(self) -> bool:
        """Returns False because ConstVar never changes"""
        return False

    def reset(self) -> None:
        """Does nothing because ConstVar never changes"""
        pass

    def last(self) -> bool:
        """Returns False because ConstVar never changes"""
        return False

class RangeVar(Var):
    """A Var that holds a range of vals"""

    type: str = ShiftField(eq="range")
    name: str = ShiftField(min_len=1)
    iter: Iter

    def __post_init__(self) -> None:
        """Evaluate RangeVar vals"""
        try:
            _ = str(self.iter.val)
        except TypeError:
            raise ValueError('RangeVar: could not convert _iter.val to str')



    def __str__(self) -> str:
        """Return the current val of iter as a string"""
        return str(self.iter.val)

    def count_iterations(self) -> int:
        """Return the number of iterations left in the range"""
        return self.iter.count_iterations()

    def __add__(self, other: int) -> bool:
        """Increment the range by other and return whether the range has more increments left"""
        for i in range(0, abs(other)):
            if other < 0:
                if not self.last():
                    return False
            else:
                if not self.next():
                    return False
        return True

    def __sub__(self, other: int) -> bool:
        """Decrement the range by other and return whether the range has more decrements left"""
        return self.__add__(-other)

    def next(self) -> bool:
        """Increment the range and return whether the range has more increments left"""
        return self.iter.next()

    def reset(self) -> None:
        """Wraps the range"""
        self.iter.reset()

    def last(self) -> bool:
        """Decrement the range and return whether the range has more decrements left"""
        return self.iter.last()

    def __iter__(self) -> Iter:
        """Used to iterate over `for item in instance` syntax"""
        return self.iter

    def __next__(self) -> Any:
        """Used by iterables to get the next val until StopIteration is raised"""
        return self.iter.next()

class ListVar(Var):
    """A Var that holds a list of values"""

    type: str = ShiftField(eq="list")
    name: str = ShiftField(min_len=1)
    vals: list[Any]
    _iter: Iter

    def __post_init__(self) -> None:
        """Set ListVar vals"""
        self._iter = Iter(**{'start': 0, 'end': len(self.vals) - 1, 'step': 1})



    def __str__(self) -> str:
        """Return the current val as a str"""
        return str(self.vals[self._iter.val])

    def count_iterations(self) -> int:
        """Return the number of vals left to iterate over"""
        return self._iter.count_iterations()

    def __add__(self, other: int) -> bool:
        """Increment the list by other and return whether the list has more increments left"""
        for i in range(0, abs(other)):
            if other < 0:
                if not self.last():
                    return False
            else:
                if not self.next():
                    return False
        return True

    def __sub__(self, other: int) -> bool:
        """Decrement the list by other and return whether the list has more decrements left"""
        return self.__add__(-other)

    def next(self) -> bool:
        """Increment the list and return whether the list has more increments left"""
        return self._iter.next()

    def reset(self) -> None:
        """Wrap the list"""
        self._iter.reset()

    def last(self) -> bool:
        """Decrement the list and return whether the list has more decrements left"""
        return self._iter.last()

    def __iter__(self) -> ListVar:
        """Used to iterate over `for item in instance` syntax"""
        return self

    def __next__(self) -> Any:
        """Used by iterables to get the next val until StopIteration is raised"""
        if self._iter.count_iterations() == 0:
            raise StopIteration
        val = self.vals[self._iter.val]
        self._iter.next()
        return val

class TimeVar(Var):
    """A Var that evaluates the current time/date"""

    type: str = ShiftField(eq="time")
    name: str = ShiftField(min_len=1)
    mode: Literal['date', 'time', 'datetime', 'iso', 'custom', ''] = None
    fmt: str | None

    @shift_repr('fmt')
    def _repr_fmt(self) -> str | None:
        if self.mode == 'custom':
            return f"fmt={self.fmt}"
        return None

    @shift_serializer('fmt')
    def _serialize_fmt(self) -> dict[str, str] | None:
        if self.mode == 'custom':
            return { 'fmt': self.fmt }
        return None


    def __post_init__(self) -> None:
        """Set the format and check vals"""
        if self.mode is None or self.mode == 'custom' or self.mode == '':
            try:
                _ = str(self)
            except ValueError:
                raise ValueError(f"TimeVar: invalid fmt string {self.fmt}")
        elif self.mode == 'date':
            self.fmt = '%Y-%m-%d'
        elif self.mode == 'time':
            self.fmt = '%H:%M:%S'
        elif self.mode == 'datetime':
            self.fmt = '%Y-%m-%d %H:%M:%S'
        elif self.mode == 'iso':
            self.fmt = '%Y-%m-%dT%H:%M:%S'



    def __str__(self) -> str:
        """Return the current time as a formatted string"""
        return datetime.now().strftime(self.fmt)

    def count_iterations(self) -> int:
        """Return 0 because TimeVar does not have any iterations"""
        return 0

    def next(self) -> bool:
        """Return False because TimeVar does not have any iterations"""
        return False

    def reset(self) -> None:
        """Do nothing because TimeVar does not have any iterations"""
        pass

    def last(self) -> bool:
        """Return False because TimeVar does not have any iterations"""
        return False

class LinkVar(Var):
    """A Var that can link to and evaluate runtime variables"""

    type: str = ShiftField(eq="link")
    name: str = ShiftField(min_len=1)
    link: Link

    def __post_init__(self) -> None:
        """Test link value"""
        try:
            _ = str(self)
        except Exception as e:
            raise ValueError(f"LinkVar: failed it evaluate link: {e}")



    def __str__(self) -> str:
        """Evaluates the runtime link variable against config and returns the string cast"""
        if callable(self.link.val):
            return str(self.link())
        return str(self.link.val)

    def count_iterations(self) -> int:
        """Return 0 because LinkVar does not have any iterations"""
        return 0

    def next(self) -> bool:
        """Return False because LinkVar does not have any iterations"""
        return False

    def reset(self) -> None:
        """Do nothing because LinkVar does not have any iterations"""
        pass

    def last(self) -> bool:
        """Return False because LinkVar does not have any iterations"""
        return False



# Trace Class
############################################################

class Trace(Shift):
    """A class that can be used to create lists of combined vars or to inherit startrace pattern functionality"""

    trace: str
    vars: dict[str, Var] = ShiftField(validator=lambda instance, var: True, validator_skips=True)
    links: dict[str, Link | dict[str, Any]] = {}
    _iter_start = False

    def __post_init__(self) -> None:
        """Build and check vars"""

        vars: dict[str, Var] = {}
        for raw_var in self.vars: # Right now self.vars is a list[dict[str, Any]]
            # Handle name collisions
            name = raw_var.get('name')
            if name is None or len(name) == 0:
                raise ValueError(f"Trace: invalid var name: {name}")
            if name in vars:
                raise ValueError(f"Trace: var {name} already exists")

            # Handle link bindings
            if isinstance(raw_var, LinkVar):
                if raw_var.name not in self.links:
                    raise ValueError(f"Trace: link var {raw_var.name} does not exist in links")
                raw_var.link = self.links[raw_var.name]
            elif isinstance(raw_var, dict) and raw_var.get('type') == 'link':
                link_name = raw_var.get('name')
                if link_name not in self.links:
                    raise ValueError(f"Trace: link var {link_name} does not exist in links")
                raw_var['link'] = self.links[link_name]

            # Build new one if raw_var is a dict, otherwise store the value
            if isinstance(raw_var, dict):
                vars[name] = build_var_from_var_type_registry(**raw_var)
            else:
                vars[name] = raw_var
        self.vars = vars

        try:
            _ = str(self)
        except Exception as e:
            raise ValueError(f"Trace: failed to evaluate: {e}")



    def eval(self) -> str:
        """Returns the string evaluation of the trace"""
        return str(self)

    def __str__(self) -> str:
        """Returns the string evaluation of the trace against vars"""
        return self.trace.format(**self.vars)

    def __len__(self) -> int:
        """Return the number of possible string evaluations left"""
        return self.count_iterations()

    def count_iterations(self) -> int:
        """Return the number of possible string evaluations left"""
        iterations = 1
        for _, var in self.vars.items():
            i = var.count_iterations()
            if i == 0:
                continue
            iterations *= i
        return iterations

    def __add__(self, other: int) -> bool:
        """Increment this instance by other and return whether this instance has more increments left"""
        for i in range(0, abs(other)):
            if other < 0:
                if not self.last():
                    return False
            else:
                if not self.next():
                    return False
        return True

    def __sub__(self, other) -> bool:
        """Decrement this instance by other and return whether this instance has more decrements left"""
        return self.__add__(-other)

    def next(self) -> bool:
        """Increment this instance and return whether this instance has more increments left"""
        for _, var in self.vars.items():
            if var.next():
                return True
            else:
                var.reset()
        return False

    def reset(self) -> None:
        """Wrap all vars"""
        for _, var in self.vars.items():
            var.reset()

    def last(self) -> bool:
        """Decrement this instance and return whether this instance has more decrements left"""
        for _, var in self.vars.items():
            if var.last():
                return True
        return False

    def __iter__(self) -> Trace:
        """Used to iterate over `for item in instance` syntax"""
        self._iter_start = True # Set flag to use current values
        return self

    def __next__(self) -> str:
        """Used by iterables to get the next eval until StopIteration is raised"""
        if self._iter_start:
            self._iter_start = False
            return str(self)
        if self.next():
            return str(self)
        raise StopIteration



# Function Utilities
########################################################################################################################



## Var type registry
############################################################

_var_type_registry: dict[str, Any] = {}

def reset_var_type_registry() -> None:
    """Reset var type registry to default vals (builtin types)"""
    global _var_type_registry
    _var_type_registry.clear()
    _var_type_registry = {
        'const': ConstVar,
        'range': RangeVar,
        'list': ListVar,
        'time': TimeVar,
        'link': LinkVar,
    }

def register_var_type_registry(typ: str, var: Any) -> None:
    """Register var type to the var type registry"""
    global _var_type_registry
    _var_type_registry[typ] = var

def remove_var_type_registry(typ: str) -> None:
    """Remove var type from the var type registry (if it exists)"""
    global _var_type_registry
    if typ not in _var_type_registry:
        return
    del _var_type_registry[typ]

def copy_var_type_registry() -> dict[str, Any]:
    """Copy the var type registry"""
    global _var_type_registry
    return _var_type_registry.copy()

def clear_var_type_registry() -> None:
    """Clear the var type registry"""
    global _var_type_registry
    _var_type_registry.clear()

def build_var_from_var_type_registry(**data) -> Var:
    """Build a Var instance based on the type in data"""
    if 'type' not in data:
        raise KeyError('type is missing')
    global _var_type_registry
    if data['type'] not in _var_type_registry:
        raise KeyError(f'type {data["type"]} is not registered')
    return _var_type_registry[data['type']](**data)



## Global
############################################################

def reset_startrace() -> None:
    reset_var_type_registry()

reset_startrace()