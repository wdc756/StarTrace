# Imports
########################################################################################################################




# Class utils
from typing import Any
from abc import ABC, abstractmethod, abstractclassmethod
from starshift import Shift, ShiftField, shift_validator, shift_setter, shift_repr, shift_serializer

# Used to get date and time for some vars
from datetime import datetime




# Utilities
########################################################################################################################



## Configs
############################################################

class VarConfig(Shift):
    """A set of config options to change how Var classes work

    Attributes:

    """

    verbosity: int = 0
    wrap: bool = True
    lazy: bool = False

DEFAULT_Var_CONFIG = VarConfig()

class PatternConfig(Shift):
    """A set of config options to change how Trace classes work

    Attributes:

    """

    verbosity: int = 0
    allow_arbitrary_code: bool = False

DEFAULT_PATTERN_CONFIG = PatternConfig()



## Helper Classes
############################################################

class Iter(Shift):
    """Iterates over a range of values"""

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

        # If step +, val must be > start and < end
        if self.step > 0:
            if self.val < self.start:
                raise ValueError("Iter: val must be > start.")
            if self.val > self.end:
                raise ValueError("Iter: val must be < end.")
        # If step -, val must be < start and > end
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

    @shift_validator('val')
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

    def wrap(self) -> None:
        """Resets the val to the opposite bound"""
        if self.end <= self.val:
            self.val = self.start
        else:
            self.val = self.end

class Link:
    """A mutable object wrapper for LinkTokens"""

    val: Any



    def __call__(self, *args, **kwargs):
        """If v is callable, call it; otherwise return the val"""
        if callable(self.val):
            return self.val(*args, **kwargs)
        return self.val

    def get(self) -> Any:
        """Return the val"""
        return self.val

    def set(self, val: Any) -> None:
        """Set the val"""
        self.val = val



# Var Classes
########################################################################################################################



class Var(Shift, ABC):
    """An abstract interface for all Vars to inherit"""

    type: str



    @abstractmethod
    def __str__(self) -> str:
        """Return the string evaluation of the Var"""
        pass

    def __len__(self) -> int:
        """Return the length of the val/values in this instance"""
        return self.count_iterations()

    @abstractmethod
    def count_iterations(self) -> int:
        """Return the number of iterations left"""
        pass

class ConstVar(Var):
    """A Var that holds a constant val"""

    val: Any

    @shift_validator('val')
    def _validate_val(self, val) -> None:
        try:
            _ = str(val)
        except TypeError:
            raise ValueError('ConstVar: could not convert val to str')



    def __str__(self) -> str:
        """Return the string evaluation of the ConstVar"""
        return str(self.val)

    def count_iterations(self) -> int:
        """Returns 0 because ConstVar never changes"""
        return 0

class RangeVar(Var):
    """A Var that holds a range of values"""

    type: str = ShiftField(eq="range")
    iter: Iter

    def __post_init__(self) -> None:
        """Evaluate RangeVar values"""
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
    values: list[Any]
    _iter: Iter

    def __post_init__(self) -> None:
        """Set ListVar values"""
        self._iter = Iter(**{'start': 0, 'end': len(self.values), 'step': 1})



    def __str__(self) -> str:
        """Return the current val as a str"""
        return self.values[self._iter.val]

    def count_iterations(self) -> int:
        """Return the number of values left to iterate over"""
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
        val = self.values[self._iter.val]
        self._iter.next()
        return val

class TimeVar(Var):
    """A Var that evaluates the current time/date"""

class LinkVar(Var):
    """A Var that can link to and evaluate runtime variables"""



# Trace Class(es)?
########################################################################################################################



class Trace(Shift):
    """A class that can be used to create lists of combined Vars or to inherit startrace pattern functionality"""



    trace: str
    Vars: list[Var] = None



    def __post_init__(self, data: dict[str, Any]) -> None:
        """Evaluate trace and Vars against config"""
        pass



    def eval(self) -> str:
        """Returns the string evaluation of the trace"""
        return str(self)

    def __str__(self) -> str:
        """Returns the string evaluation of the trace against Vars"""
        pass

    def __len__(self) -> int:
        """Return the number of possible string evaluations left or the number of Vars or the len of trace"""
        if self.next() and self.last():
            return self.len_iterations()
        elif self.Vars:
            return self.len_Vars()
        else:
            return self.len_template()

    def len_iterations(self) -> int:
        """Return the number of possible string evaluations left"""
        iterations = 1
        for Var in self.Vars:
            iterations *= Var.count_iterations()
        return iterations

    def len_Vars(self) -> int:
        """Return the number of Vars"""
        return len(self.Vars)

    def len_template(self) -> int:
        """Return the length of the trace"""
        return len(self.trace)

    def __add__(self, other: int) -> bool:
        """Increment this instance by int and return whether this instance has more increments left"""
        # If subclass, pass
        # Else recursive increment - for other
        pass

    def next(self) -> bool:
        """Increment this instance and return whether this instance has more increments left"""
        # If subclass, pass
        # Else recursive increment
        pass

    def __sub__(self, other) -> bool:
        """Decrement this instance by int and return whether this instance has more decrements left"""
        return self.__add__(-other)

    def last(self) -> bool:
        """Decrement this instance and return whether this instance has more decrements left"""
        # If subclass, pass
        # Else recursive decrement
        pass

    def __iter__(self) -> Trace:
        """Used to iterate over `for item in instance` syntax"""
        return self

    def __next__(self) -> str:
        """Used by iterables to get the next eval until StopIteration is raised"""
        if self.next():
            return str(self)
        raise StopIteration



# Registries
########################################################################################################################



## Var type registry
############################################################

_var_type_registry: dict[str, Any] = {}

def reset_var_type_registry() -> None:
    """Reset var type registry to default values (builtin types)"""
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