# Imports
########################################################################################################################



# Used to create abstract token base class
from abc import ABC, ABCMeta, abstractmethod

# Used to create type hints
from typing import Any, List, Union

# Used to get date and time for Date/Time Tokens
from datetime import datetime



# Misc Classes
########################################################################################################################



class Iter:
    """Iterates over a range of values"""
    value: Any
    start: Any
    end: Any
    step: Any

    def __init__(self, value: Any, start: Any, end: Any, step: Any) -> None:
        self.value = value
        self.start = start
        self.end = end
        self.step = step

        self.__post_init__()

    def __post_init__(self):
        if self.value < self.start:
            raise ValueError("Iter: value must be > start.")
        if self.value > self.end:
            raise ValueError("Iter: value must be < end.")
        if self.step == 0:
            raise ValueError("Iter: step cannot be zero.")

        if self.start == self.end:
            raise ValueError("Iter: start and end cannot be equal.")
        if self.start > self.end and self.step > 0:
            raise ValueError("Iter: start must be < end when stepping up.")
        if self.start < self.end and self.step < 0:
            raise ValueError("Iter: start must be > end when stepping down.")



    def next(self) -> bool:
        """Increments the current iterator value to the next and returns True if it had space to increment, False otherwise"""
        if self.value < self.end:
            self.value += self.step
            return True
        else:
            self.value = self.start
            return False

    def last(self) -> bool:
        """Decrement the current token value to the last and returns True if it had space to decrement, False otherwise"""
        if self.value > self.start:
            self.value -= self.step
            return True
        else:
            self.value = self.end
            return False



# Tokens
########################################################################################################################



class TokenMeta(ABCMeta):
    """Metaclass for Token, used to route __new__ to the correct subclass (or at least tell the IDE that's what's happening)"""

    def __call__(cls, *args, **kwargs):
        # Allow Token() instantiation by routing __new__ manually
        if cls is Token:
            return Token.__new__(Token, *args, **kwargs)
        return super().__call__(*args, **kwargs)

class Token(ABC, metaclass=TokenMeta):
    """Abstract base class for all tokens - will automatically route to the correct subclass based on the constructor arguments"""

    def __new__(cls, *args, **kwargs):
        # If not Token, route to the correct subclass
        if cls is not Token:
            return super().__new__(cls)

        # No args: invalid
        if not args:
            raise ValueError("Token: no arguments provided.")

        # Mono-argument routing
        if len(args) == 1:
            a0 = args[0]

            # ListToken when a0 is a list
            if isinstance(a0, list):
                return ListToken(a0)

            # Dict-based input when a0 is a dict
            elif isinstance(a0, dict):
                if "type" not in a0:
                    raise TypeError("Token: dict-based input must have a 'type' key.")

                if a0["type"] == "const":
                    if "value" not in a0:
                        raise TypeError("Token: dict-based input for ConstToken must have a 'value' key.")
                    return ConstToken(a0["value"])
                if a0["type"] == "list":
                    if "values" not in a0:
                        raise TypeError("Token: dict-based input for ListToken must have a 'values' key.")
                    return ListToken(a0["values"])
                elif a0["type"] == "range":
                    if "start" not in a0 or "end" not in a0 or "step" not in a0:
                        raise TypeError("Token: dict-based input for RangeToken must have 'start', 'end', and 'step' keys.")
                    return RangeToken(a0["start"], a0["end"], a0["step"])
                elif a0["type"] == "time":
                    if "mode" not in a0:
                        raise TypeError("Token: dict-based input for TimeToken must have a 'mode' key.")
                    if a0["mode"] == "custom":
                        if "fmt" not in a0:
                            raise TypeError("Token: dict-based input for TimeToken with custom mode must have a 'fmt' key.")
                        return TimeToken(a0["mode"], a0["fmt"])
                    else:
                        return TimeToken(a0["mode"])
                elif a0["type"] == "link":
                    # Note this will raise an error because 'eval_allowed' is False by default
                    if "link" not in a0 or "context" not in a0:
                        raise TypeError("Token: dict-based input for LinkToken must have 'link' and 'context' keys.")
                    return LinkToken(a0["link"], a0["context"])
                else:
                    raise TypeError(f"Token: dict-based token invalid type: {a0['type']}")

            # Else TimeToken or ConstToken
            else:
                # TimeToken when a0 is a string matching the TimeToken modes
                if a0 in ("date", "time", "datetime", "iso"):
                    return TimeToken(a0)
                # Else assume ConstToken
                return ConstToken(a0)

        # Dual-argument routing
        elif len(args) == 2:
            a0, a1 = args

            # Dict-Based LinkToken when a0 is a dict and a1 is a bool
            if isinstance(a0, dict) and isinstance(a1, bool):
                if "link" not in a0 or "context" not in a0:
                    raise TypeError("Token: dict-based input for LinkToken must have 'link' and 'context' keys.")
                return LinkToken(a0["link"], a0["context"], a1)

            # TimeToken when a0 is "custom" and a1 is a string
            if isinstance(a0, str) and a0 == "custom" and isinstance(a1, str):
                return TimeToken(a0, a1)

            # LinkToken when a0 is a string and a1 is a dict
            elif isinstance(a0, str) and isinstance(a1, dict):
                # Note this will raise an error because 'eval_allowed' is False by default
                return LinkToken(a0, a1)

        # Tri-argument routing
        elif len(args) == 3:
            a0, a1, a2 = args

            # LinkToken when a0 is a dict (link Token dict), a1 is a dict (global context, and a2 is a bool (can eval)
            if isinstance(a0, dict) and isinstance(a1, dict) and isinstance(a2, bool):
                if "link" not in a0:
                    raise TypeError("Token: dict-based input for LinkToken must have 'link' and keys.")
                if "context" in a0:
                    a1.update(a0["context"]) # Add per-token context to global context
                return LinkToken(a0["link"], a1, a2)
            # LinkToken when a0 is a str (str symbol link), a1 is a dict (global context, and a2 is a bool (can eval)
            if isinstance(a0, str) and isinstance(a1, dict) and isinstance(a2, bool):
                return LinkToken(a0, a1, a2)

            # Else assume RangeToken
            else:
                return RangeToken(a0, a1, a2)

        # If we got here, no match was found
        raise TypeError(f"Token: invalid argument combination: {args}")

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the token"""
        pass

    @abstractmethod
    def __post_init__(self) -> None:
        """Check token values"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return the string evaluation of the token"""
        return self.evaluate()

    @abstractmethod
    def __len__(self) -> int:
        """Return the length of the token (length of const string value or length of the list)"""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """Return a constructor call that can be used to recreate this token"""
        pass



    @abstractmethod
    def to_dict(self) -> dict:
        """Return a dictionary representation of the token that can be used to recreate it"""
        pass

    @abstractmethod
    def evaluate(self) -> str:
        """Return the string evaluation of the token"""
        pass

    @abstractmethod
    def next(self) -> bool:
        """Increments the current token value to the next and returns True if it had space to increment, False otherwise."""
        pass

    @abstractmethod
    def last(self) -> bool:
        """Decrement the current token value to the last and returns True if it had space to decrement, False otherwise."""
        pass

class ConstToken(Token):
    """Token representing a constant string value"""

    def __init__(self, value: Any) -> None:
        self.value = value

        self.__post_init__()

    def __post_init__(self) -> None:
        try:
            self.value = str(self.value)
        except Exception as e:
            raise TypeError(f"ConstToken: value must be castable to a string. Error: {e}")

    def __str__(self) -> str:
        return self.evaluate()

    def __len__(self) -> int:
        return len(self.value)

    def __repr__(self) -> str:
        return f'ConstToken({self.value})'



    def to_dict(self) -> dict:
        return {
            "type": "const",
            "value": self.value
        }

    def evaluate(self) -> str:
        return self.value

    def next(self) -> bool:
        return False

    def last(self) -> bool:
        return False

class ListToken(Token):
    """Token representing a list of values"""

    def __init__(self, values: List[Any]) -> None:
        self.values = values
        self.iter = Iter(0, 0, len(values) - 1, 1)

        self.__post_init__()

    def __post_init__(self) -> None:
        if len(self.values) == 0:
            raise ValueError("ListToken: values cannot be empty.")
        try:
            str(self.values[0])
        except Exception as e:
            raise TypeError(f"ListToken: values must be castable to a string. Error: {e}")

    def __str__(self) -> str:
        return self.evaluate()

    def __len__(self) -> int:
        return len(self.values)

    def __repr__(self) -> str:
        return f'ListToken({self.values})'


    def to_dict(self) -> dict:
        return {
            "type": "list",
            "values": self.values
        }

    def evaluate(self) -> str:
        return str(self.values[self.iter.value])

    def next(self) -> bool:
        return self.iter.next()

    def last(self) -> bool:
        return self.iter.last()

class RangeToken(Token):
    """Token representing a range of values"""

    def __init__(self, start: Any, end: Any, step: Any) -> None:
        self.iter = Iter(start, start, end, step)

        self.__post_init__()

    def __post_init__(self) -> None:
        try:
            str(self.iter.value)
        except Exception as e:
            raise TypeError(f"RangeToken: start, end, and step must be castable to a string. Error: {e}")

    def __str__(self) -> str:
        return self.evaluate()

    def __len__(self) -> int:
        return (self.iter.end - self.iter.start) // self.iter.step + 1

    def __repr__(self) -> str:
        return f'RangeToken({self.iter.start}, {self.iter.end}, {self.iter.step})'



    def to_dict(self) -> dict:
        return {
            "type": "range",
            "start": self.iter.start,
            "end": self.iter.end,
            "step": self.iter.step
        }

    def evaluate(self) -> str:
        return str(self.iter.value)

    def next(self) -> bool:
        return self.iter.next()

    def last(self) -> bool:
        return self.iter.last()

class TimeToken(Token):
    """Token representing a date/time"""

    def __init__(self, mode: str, fmt: str=None) -> None:
        self.mode = mode
        self.fmt = fmt

        if self.mode == "date":
            self.fmt = "%Y-%m-%d"
        elif self.mode == "time":
            self.fmt = "%H:%M:%S"
        elif self.mode == "datetime":
            self.fmt = "%Y-%m-%d_%H:%M:%S"
        elif self.mode == "iso":
            self.fmt = "%Y-%m-%dT%H:%M:%S"

        self.__post_init__()

    def __post_init__(self) -> None:
        valid_modes = ["date", "time", "datetime", "iso", "custom"]
        if self.mode not in valid_modes:
            raise ValueError(f"TimeToken: Invalid mode: {self.mode}. Valid modes are: {valid_modes}")
        if self.mode == "custom" and self.fmt is None:
            raise ValueError("TimeToken: Custom mode requires a format string.")
        if self.mode == "custom":
            try:
                datetime.now().strftime(self.fmt)
            except Exception as e:
                raise ValueError(f"TimeToken: Invalid custom format string: {self.fmt}. Error: {e}")

    def __str__(self) -> str:
        return self.evaluate()

    def __len__(self) -> int:
        return 0

    def __repr__(self) -> str:
        if self.mode == "custom":
            return f'TimeToken({self.mode}, {self.fmt})'
        return f'TimeToken("{self.mode}")'



    def to_dict(self) -> dict:
        if self.mode == "custom":
            return {
                "type": "time",
                "mode": self.mode,
                "fmt": self.fmt
            }
        return {
            "type": "time",
            "mode": self.mode
        }

    def evaluate(self) -> str:
        return datetime.now().strftime(self.fmt)

    def next(self) -> bool:
        return False

    def last(self) -> bool:
        return False

class LinkToken(Token):
    """Token that links to a runtime variable or function, using a safe read-only context"""

    def __init__(self, link: str, context: dict[str, Any], eval_allowed: bool=False) -> None:
        self._link = link
        self._context = dict(context) # Shallow copy to avoid runtime tampering
        self._eval_allowed = eval_allowed

        if not self._eval_allowed:
            raise ValueError("LinkToken: eval_allowed must be True to enable arbitrary code execution.")

        self.__post_init__()

    def __post_init__(self) -> None:
        if self._link == "":
            raise ValueError("LinkToken: link cannot be an empty string.")

        try:
            eval(self._link, {"__builtins__": {}}, self._context)
        except Exception as e:
            raise ValueError(f"LinkToken: link '{self._link}' is not a valid expression or is missing context. Error: {e}")

        try:
            str(eval(self._link, {"__builtins__": {}}, self._context))
        except Exception as e:
            raise ValueError(f"LinkToken: value of link '{self._link}' does not have a valid __str__ method. Error: {e}")

    def __str__(self) -> str:
        return self.evaluate()

    def __len__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return f'LinkToken({self._link}, {self._context})'



    def to_dict(self) -> dict:
        return {
            "type": "link",
            "link": self._link,
            "context": self._context
        }

    def evaluate(self) -> str:
        if not self._eval_allowed:
            raise ValueError("LinkToken: eval_allowed must be True to enable arbitrary code execution.")
        try:
            return str(eval(self._link, {"__builtins__": {}}, self._context))
        except Exception as e:
            raise RuntimeError(f"LinkToken: eval failed for '{self._link}': {e}")

    def next(self) -> bool:
        return False

    def last(self) -> bool:
        return False



# Pattern
########################################################################################################################



class Pattern:
    """List of tokens that are joined together to form a pattern"""

    def __init__(self, tokens: Union[List[Any], dict], global_context: dict[str, Any]=None, eval_allowed: bool=None) -> None:
        self._global_context = global_context
        self._eval_allowed = eval_allowed
        self.tokens = []
        if isinstance(tokens, List):
            for tok in tokens:
                # if already a Token subclass, append
                if isinstance(tok, Token):
                    self.tokens.append(tok)
                # Else send args to Token constructor
                else:
                    self.tokens.append(Token(tok))
        else: # Assume dict
            # Get global context and eval_allowed from the main dict if present - but if we pass args in to Pattern(), those take precedence
            if self._global_context is None:
                try:
                    self._global_context = tokens["global_context"]
                except KeyError:
                    pass
            if self._eval_allowed is None:
                try:
                    self._eval_allowed = tokens["eval_allowed"]
                except KeyError:
                    pass

            for tok in tokens["tokens"]:
                # If token is link, we need to pass global context and eval_allowed to Token constructor
                try:
                    if tok.get("type") == "link":
                        self.tokens.append(Token(tok, self._global_context, self._eval_allowed))
                        continue
                except AttributeError:
                    pass # We can pass here, because Token().__new__ will handle missing dict key errors
                self.tokens.append(Token(tok))

    def __str__(self) -> str:
        return self.evaluate()

    def __len__(self) -> int:
        return len(self.tokens)

    def __repr__(self) -> str:
        return f"Pattern({self.tokens.__repr__()})"

    def __add__(self, other: int) -> None:
        if other < 0:
            for _ in range(-other):
                self.last()
            return
        for _ in range(other):
            self.next()

    def __sub__(self, other: int) -> None:
        self.__add__(-other)



    def to_dict(self) -> dict:
        return {
            "tokens": self.tokens
        }

    def evaluate(self) -> str:
        res = ""
        for tok in self.tokens:
            res += str(tok)
        return res

    def next(self) -> bool:
        for tok in reversed(self.tokens):
            if tok.next():
                return True
        return False

    def last(self) -> bool:
        for tok in reversed(self.tokens):
            if tok.last():
                return True
        return False