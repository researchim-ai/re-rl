"""Strict pair parsing for grid answers; malformed tails cannot be discarded."""
import re
from re_rl.tasks.math.logic import _logic_utils as U


def parse_coordinates(prediction,empty_labels=()):
    text = U.clean(prediction).strip().lower().rstrip(" .;!")
    if text in {*(label.lower() for label in empty_labels)} or ''.join(text.split()) in {'[]','{}','∅'}:
        return set()
    if re.search(r'\d+\.\d+|\d+\s*/\s*\d+',text):
        return None
    values = U.parse_ints(text)
    if not values or len(values)%2:
        return None
    pairs = [(values[i]-1,values[i+1]-1) for i in range(0,len(values),2)]
    if len(set(pairs)) != len(pairs): return None
    return set(pairs)
