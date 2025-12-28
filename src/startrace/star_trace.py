# Imports
########################################################################################################################




# Used to create type hints
from typing import Any, List, Union

# Used to get date and time for Date/Time Bindings
from datetime import datetime

# Used to validate data automatically
from starshift import *



# Misc Classes
########################################################################################################################



DEFAULT_STARTRACE_SHIFT_CONFIG = ShiftConfig()

class BindingConfig(Shift):
    """A set of config options to change how Binding classes work

    Attributes:

    """

    __shift_config__: ShiftConfig = ShiftConfig(do_validation=False)

    verbosity: int = 0
    iterables_wrap_around: bool = True
    lazy_binding: bool = False

    shift_config: ShiftConfig = DEFAULT_STARTRACE_SHIFT_CONFIG

DEFAULT_BINDING_CONFIG = BindingConfig()

class PatternConfig(Shift):
    """A set of config options to change how Pattern classes work

    Attributes:

    """

    __shift_config__: ShiftConfig = ShiftConfig(do_validation=False)

    verbosity: int = 0
    allow_arbitrary_code: bool = False
    allow_per_bind_context: bool = False

    pattern_binding_config_has_precedence: bool = False
    binding_config: BindingConfig = DEFAULT_BINDING_CONFIG

    pattern_shift_config_has_precedence: bool = False
    shift_config: ShiftConfig = DEFAULT_STARTRACE_SHIFT_CONFIG

DEFAULT_PATTERN_CONFIG = PatternConfig()

class Iter(Shift):
    """Iterates over a range of values"""

    __shift_config__: ShiftConfig = DEFAULT_STARTRACE_SHIFT_CONFIG



    value: Any = None
    start: Any
    end: Any
    step: Any



    def __post_init__(self, data: dict[str, Any]) -> None:
        # Automatically set value if not provided
        if self.value is None:
            self.value = self.start

        # Make sure whatever types value and step are, they can be added together
        try:
            _ = self.value + self.step
        except Exception as e:
            raise TypeError(f"Iter: could not increment value by step")

        # Make sure whatever types value, start, and end are they can be compared
        try:
            _ = self.value <= self.start
            _ = self.value <= self.end
            _ = self.value <= self.step
        except Exception as e:
            raise TypeError("Iter: could not compare value, start, end, or step")

        # If step is 0, we can't progress, so throw
        if self.step == 0:
            raise ValueError("Iter: step cannot be zero.")

        # If step +, value must be > start and < end
        if self.step > 0:
            if self.value < self.start:
                raise ValueError("Iter: value must be > start.")
            if self.value > self.end:
                raise ValueError("Iter: value must be < end.")
        # If step -, value must be < start and > end
        else:
            if self.value > self.start:
                raise ValueError("Iter: value must be < start.")
            if self.value < self.end:
                raise ValueError("Iter: value must be > end.")

        # If start > end and step > 0 the range is invalid, so throw
        if self.start > self.end and self.step > 0:
            raise ValueError("Iter: start must be < end when stepping up.")
        # If start < end and step < 0 the range is invalid, so throw
        if self.start < self.end and self.step < 0:
            raise ValueError("Iter: start must be > end when stepping down.")



    @shift_serializer('value')
    @shift_repr('value')
    def _repr_value(self, field: str, val: Any, default: Any) -> Union[str, None]:
        if val != default:
            return f"{val}"
        return None



    def __len__(self) -> Union[int, None]:
        """Return the number of iterations left in the range"""
        return self.count_iterations()

    def count_iterations(self) -> int:
        """Return the number of iterations left in the range"""
        return (self.end - self.value) // self.step

    def next(self) -> bool:
        """Increments the current iterator value to the next and returns True if it had space to increment, False otherwise"""
        if self.step > 0:
            if self.value < self.end:
                self.value += self.step
                return True
            else:
                return False
        else:
            if self.value > self.end:
                self.value += self.step
                return True
            else:
                return False

    def last(self) -> bool:
        """Decrement the current token value to the last and returns True if it had space to decrement, False otherwise"""
        if self.step > 0:
            if self.value > self.start:
                self.value -= self.step
                return True
            else:
                return False
        else:
            if self.value < self.start:
                self.value -= self.step
                return True
            else:
                return False

    def wrap(self) -> None:
        """Resets the value to the opposite bound"""
        if self.end <= self.value:
            self.value = self.start
        else:
            self.value = self.end

    def __iter__(self) -> Iter:
        """Used to iterate over `for item in instance` syntax"""
        return self

    def __next__(self) -> Any:
        """Used by iterables to get the next value until StopIteration is raised"""
        if self.count_iterations() == 0:
            raise StopIteration
        val = self.value
        self.next()
        return val

class Link(Shift):
    """A mutable object wrapper for LinkTokens"""

    # This class doesn't really need to validate anything, as LinkToken does all the validation, but it's still
    #   useful for this to be a Shift class, so se can recursively set it from other Shift subclasses
    __shift_config__: ShiftConfig = ShiftConfig(do_validation=False)



    value: Any



    def __call__(self, *args, **kwargs):
        """If v is callable, call it; otherwise return the value"""
        if callable(self.value):
            return self.value(*args, **kwargs)
        return self.value

    def get(self) -> Any:
        """Return the value"""
        return self.value

    def set(self, value: Any) -> None:
        """Set the value"""
        self.value = value



# Binding Classes
########################################################################################################################



class Binding(Shift):
    """An abstract interface for all Bindings to inherit"""

    __binding_config__: BindingConfig = DEFAULT_BINDING_CONFIG



    type: str



    def __post_init__(self, data: dict[str, Any]) -> None:
        """Evaluate Binding values"""
        pass



    def __str__(self) -> str:
        """Return the string evaluation of the Binding"""
        pass

    def __len__(self) -> Union[int, None]:
        """Return the length of the value/values in this instance"""
        pass

    def count_iterations(self) -> int:
        """Return the number of iterations left"""
        pass

    def __add__(self, other: int) -> bool:
        """Increment this instance by int and return whether this instance has more increments left"""
        for i in range(0, abs(other)):
            if other < 0:
                if not self.last():
                    return False
            else:
                if not self.next():
                    return False
        return True

    def next(self) -> bool:
        """Increment this instance and return whether this instance has more increments left"""
        pass

    def __sub__(self, other) -> bool:
        """Decrement this instance by int and return whether this instance has more decrements left"""
        return self.__add__(-other)

    def last(self) -> bool:
        """Decrement this instance and return whether this instance has more decrements left"""
        pass

    def __iter__(self) -> Any:
        """Used to iterate over `for item in instance` syntax"""
        pass

    def __next__(self) -> Any:
        """Used by iterables to get the next value until StopIteration is raised"""
        pass



class RangeBinding(Binding):
    """A binding that holds a range of values"""

    __binding_config__: BindingConfig = DEFAULT_BINDING_CONFIG



    type: str = "range"
    iter: Iter



    @shift_validator('type')
    def _validate_type(self, data: dict[str, Any], field: str) -> bool:
        if data.get('type') is not None and data.get('type') != "range":
            raise ValueError("RangeBinding: type must be 'range'")
        return True

    @shift_validator('iter')
    def _validate_iter(self, data: dict[str, Any], field: str) -> bool:
        try:
            _ = str(data['iter']['value'])
        except Exception as e:
            raise ValueError("RangeBinding: iter.value must be castable to str")
        return True



    @shift_repr('type')
    @shift_serializer('type')
    def _repr_type(self, field: str, val: Any, default: Any) -> Union[str, None]:
        return "range"



    def __str__(self) -> str:
        """Return the current value of iter as a string"""
        return str(self.iter.value)

    def __len__(self) -> Union[int, None]:
        """Return the number of iterations left in the range"""
        return self.count_iterations()

    def count_iterations(self) -> int:
        """Return the number of iterations left in the range"""
        return self.iter.count_iterations()

    def next(self) -> bool:
        """Increment this instance and return whether this instance has more increments left"""
        return self.iter.next()

    def last(self) -> bool:
        """Decrement this instance and return whether this instance has more decrements left"""
        return self.iter.last()

    def __iter__(self) -> Iter:
        """Used to iterate over `for item in instance` syntax"""
        return self.iter

class ListBinding(Binding):
    """A binding that holds a list of values"""

    __binding_config__: BindingConfig = DEFAULT_BINDING_CONFIG



    type: str = "list"
    values: list[Any]
    iter: Iter = None



    @shift_validator('type')
    def _validate_type(self, data: dict[str, Any], field: str) -> bool:
        if data.get('type') is not None and data.get('type') != "list":
            raise ValueError("ListBinding: type must be 'list'")
        return True

    @shift_validator('iter')
    def _validate_iter(self, data: dict[str, Any], field: str) -> bool:
        if data.get('iter') is not None:
            if data.get('iter').get('start') is not None and data.get('iter').get('start') != 0:
                raise ValueError("ListBinding: iter.start must be 0")
            if data.get('iter').get('end') is not None and data.get('iter').get('end') != len(data['values']):
                raise ValueError("ListBinding: iter.end must be the length of values")
            if data.get('iter').get('step') is not None and data.get('iter').get('step') != 1:
                raise ValueError("ListBinding: iter.step must be 1")
        return True

    @shift_setter('iter')
    def _set_iter(self, data: dict[str, Any], field: str) -> None:
        setattr(self, 'iter', Iter(start=0, end=len(data['values']), step=1))



    @shift_repr('type')
    @shift_serializer('type')
    def _repr_type(self, field: str, val: Any, default: Any) -> str:
        return "list"

    @shift_repr('iter')
    @shift_serializer('iter')
    def _repr_iter(self, field: str, val: Any, default: Any) -> None:
        return None



    def __str__(self) -> str:
        """Return the current value as a str"""
        return self.values[self.iter.value]

    def __len__(self) -> Union[int, None]:
        """Return the length of values"""
        return len(self.values)

    def count_iterations(self) -> int:
        """Return the number of values left to iterate over"""
        return self.iter.count_iterations()

    def next(self) -> bool:
        """Increment this instance and return whether this instance has more increments left"""
        return self.iter.next()

    def last(self) -> bool:
        """Decrement this instance and return whether this instance has more decrements left"""
        return self.iter.last()

    def __iter__(self) -> ListBinding:
        """Used to iterate over `for item in instance` syntax"""
        return self

    def __next__(self) -> Any:
        """Used by iterables to get the next value until StopIteration is raised"""
        if self.iter.count_iterations() == 0:
            raise StopIteration
        val = self.values[self.iter.value]
        self.iter.next()
        return val

class TimeBinding(Binding):
    """A binding that can capture the current time/date"""

class LinkBinding(Binding):
    """A binding that can link to and evaluate runtime variables"""



# Pattern Class(es)?
########################################################################################################################



class Pattern(Shift):
    """A class that can be used to create lists of combined bindings or to inherit startrace pattern functionality"""

    __pattern_config__: PatternConfig = DEFAULT_PATTERN_CONFIG



    template: str
    bindings: list[Binding] = None



    @shift_validator('template')
    def _validate_template(self, data: dict[str, Any], field: str) -> bool:
        if len(data['template']) == 0:
            raise ValueError("Pattern: template cannot be an empty string")
        return True

    def __post_init__(self, data: dict[str, Any]) -> None:
        """Evaluate template and bindings against config"""
        pass



    def __str__(self) -> str:
        """Returns the string evaluation of the template against bindings"""
        pass

    def __len__(self) -> int:
        """Return the number of possible string evaluations left or the number of bindings or the len of template"""
        if self.next() and self.last():
            return self.len_iterations()
        elif self.bindings:
            return self.len_bindings()
        else:
            return self.len_template()

    def len_iterations(self) -> int:
        """Return the number of possible string evaluations left"""
        iterations = 1
        for binding in self.bindings:
            iterations *= binding.count_iterations()
        return iterations

    def len_bindings(self) -> int:
        """Return the number of bindings"""
        return len(self.bindings)

    def len_template(self) -> int:
        """Return the length of the template"""
        return len(self.template)

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

    def __iter__(self) -> Pattern:
        """Used to iterate over `for item in instance` syntax"""
        return self

    def __next__(self) -> str:
        """Used by iterables to get the next value until StopIteration is raised"""
        if self.next():
            return str(self)
        raise StopIteration