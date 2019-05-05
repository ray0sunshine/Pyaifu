# custom json serializer since the other one wants to newline all the things


def jsonSerialize(o, level=0, key=''):
    ret = ''
    SP = '    '
    IN = SP * level
    if isinstance(o, dict):
        if not o:
            return '{}'
        ret += '{\n'
        ret += ',\n'.join([IN + SP + '"' + k + '": ' + jsonSerialize(v, level + 1, k) for k, v in o.items()])
        ret += '\n' + IN + '}'
    elif key == 'pixel':
        # compact special case
        ret += '[\n'
        ret += ',\n'.join(IN + SP + '{' + ', '.join('"' + k + '": [' + ', '.join(str(n) for n in list(v)) + ']' for k, v in e.items()) + '}' for e in o)
        ret += '\n' + IN + ']'
    elif isinstance(o, (list, tuple)):
        if all(isinstance(e, (int, float)) for e in o):
            ret += '[' + ', '.join(str(e) for e in list(o)) + ']'
        else:
            ret += '[\n'
            ret += ',\n'.join(IN + SP + jsonSerialize(e, level + 1) for e in o)
            ret += '\n' + IN + ']'
    elif isinstance(o, str):
        ret += '"' + o + '"'
    elif isinstance(o, (bool, int)):
        ret += str(o).lower()
    elif isinstance(o, float):
        ret += '%.4g' % o
    elif o is None:
        ret += 'null'
    return ret
