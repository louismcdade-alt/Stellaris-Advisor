"""
Minimal parser for the Paradox "Clausewitz" save format used by Stellaris.

The format is a tree of key=value pairs. Values are scalars, quoted strings,
or brace-delimited blocks. Two quirks we handle:

  * Duplicate keys at the same level (e.g. repeated `technology=` lines). We
    collect repeats into a list rather than overwriting.
  * Brace blocks that are really arrays: `colors={ "black" "black" }` or
    `random={ 0 4207665165 }`. These have no `key=` inside, so we return a list.

This is deliberately small and tolerant rather than a full grammar. Stellaris
saves are huge (20+ MB), so we expose `extract_block` to brace-match a single
top-level section and parse only that, keeping things fast.
"""

import re

# Tokens: braces, '=', quoted strings, or bare words (numbers/identifiers).
_TOKEN = re.compile(r'''
      (?P<lbrace>\{)
    | (?P<rbrace>\})
    | (?P<eq>=)
    | (?P<qstr>"(?:[^"\\]|\\.)*")
    | (?P<word>[^\s{}=]+)
''', re.VERBOSE)


def _tokenize(text):
    for m in _TOKEN.finditer(text):
        kind = m.lastgroup
        val = m.group()
        if kind == 'qstr':
            val = val[1:-1]  # strip surrounding quotes
        yield kind, val


def _coerce(word):
    """Turn a bare word into int/float/bool where it clearly is one."""
    if word == 'yes':
        return True
    if word == 'no':
        return False
    # Stellaris uses 1.2345 floats and plain ints; also negatives.
    if re.fullmatch(r'-?\d+', word):
        try:
            return int(word)
        except ValueError:
            return word
    if re.fullmatch(r'-?\d+\.\d+', word):
        return float(word)
    return word


class _Parser:
    def __init__(self, text):
        self.tokens = list(_tokenize(text))
        self.i = 0

    def _peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def parse_block(self):
        """Parse the contents of a block (caller has consumed the '{').

        Returns a dict when the block is key=value pairs, or a list when it is
        a bare array of scalars/blocks. Duplicate keys become lists.
        """
        items = []          # list of (key, value) we accumulate
        bare = []           # bare scalars (array form)
        while True:
            kind, val = self._peek()
            if kind is None or kind == 'rbrace':
                self.i += 1  # consume '}' (or stop at EOF)
                break
            if kind == 'lbrace':
                # A nested block appearing as a bare array element.
                self.i += 1
                bare.append(self.parse_block())
                continue
            # kind is word/qstr -> could be a key (if followed by '=') or a scalar
            self.i += 1
            nxt_kind, _ = self._peek()
            if nxt_kind == 'eq':
                self.i += 1  # consume '='
                value = self._parse_value()
                items.append((val if nxt_kind else val, value))
            else:
                bare.append(_coerce(val))

        if items and not bare:
            return _collapse(items)
        if bare and not items:
            return bare
        if not items and not bare:
            return {}
        # Mixed (rare) — return both under a structured shape.
        result = _collapse(items)
        result['__items__'] = bare
        return result

    def _parse_value(self):
        kind, val = self._peek()
        if kind == 'lbrace':
            self.i += 1
            return self.parse_block()
        self.i += 1
        if kind == 'qstr':
            return val
        return _coerce(val)


def _collapse(items):
    """Combine (key,value) pairs into a dict, turning duplicate keys into lists."""
    out = {}
    for k, v in items:
        if k in out:
            if isinstance(out[k], list) and getattr(out[k], '_multi', False):
                out[k].append(v)
            else:
                lst = _MultiList([out[k], v])
                out[k] = lst
        else:
            out[k] = v
    return out


class _MultiList(list):
    """A list that marks 'these are repeated-key values', so we can keep
    appending rather than mistaking it for a real array value."""
    _multi = True


def parse(text):
    """Parse a full Clausewitz document (no enclosing braces)."""
    p = _Parser('{\n' + text + '\n}')
    # prime: skip the synthetic opening brace
    p.i = 1
    return p.parse_block()


def extract_block(text, key, start=0):
    """Return the substring of the brace block for a top-level `key=` section.

    Brace-matches from the first '{' after `key`. Returns (block_text, end_index)
    or (None, -1) if not found. `block_text` includes the outer braces.
    """
    m = re.search(r'(?:^|\n)' + re.escape(key) + r'=\s*\n?\s*\{', text[start:])
    if not m:
        return None, -1
    abs_open = start + text[start:].index('{', m.start())
    depth = 0
    j = abs_open
    n = len(text)
    while j < n:
        c = text[j]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[abs_open:j + 1], j + 1
        j += 1
    return None, -1
