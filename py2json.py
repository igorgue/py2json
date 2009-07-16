"""python 2 json-schema"""

import inspect

types_dict = {"str": "string",
              "int": "integer",
              "bool": "boolean",
              "NoneType": "any",
              "float": "number",
              "classobj": "object",
              "instance": "object",
              "list": "array"}

def to_json_schema_type(t):
    """Transform a Python type to a json-schema type"""
    # we avoid "null" intentionally here, since we use "any" for 
    # "NoneType"
    if isinstance(t, type):
        return types_dict.get(t.__name__)
    elif isinstance(t, str) and types_dict.has_key(t):
        return types_dict.get(t)
    else:
        return types_dict.get(type(t).__name__)

def get_method_desc(m):
    """Get a method dict from a method:

        example: {"id": "method", "type": "object", "properties": {
                    "arg1": {"type": "type"}, "arg2": {"type": "type"} } }
    """
    if not inspect.ismethod(m):
        log_msg = "The paramether %s is not a method" % m
        log.error(log_msg)
        raise NotAMethodException(log_msg)

    # Convert default names to types and extend the defaults to a bigger
    # list
    def get_json_schema_args_types(argc, defaults):
        l = []
        if defaults:
            for i in list(defaults):
                l.append('{"type":"%s"}' % to_json_schema_type(i))
        for i in range(argc - len(l)):
            l.insert(0, '{"type":"%s"}' % to_json_schema_type(None))

        return l

    m_name = m.__name__
    args, _, _, defaults = inspect.getargspec(m)
    m_desc = '"%s":{"type":"object","properties":{' % m_name

    # some cleaning
    args = args[1:] # removing self

    # if we don't have any arguments, then just close the schema
    if not len(args):
        return m_desc + '}}'

    # getting all the types
    defaults = get_json_schema_args_types(len(args), defaults) 
    m_arguments = zip(args, defaults)

    for k, v in m_arguments:
        m_desc += '"%s":%s,' % (k, v)

    m_desc = m_desc[:-1] # removing the last comma a.k.a garbage

    # adding the last brackets close the properties and the value
    # of the class
    m_desc += "}}"

    return m_desc

def get_class_desc(c):
    """Get a class dict from a class:

        example: {"id": "class", "type": "object", "properties": 
                    {"method1": {"type": "object"}, "properties":
                        {"arg1" {"type": "type"} } },
                    {"method2": {"type": "object"}, "properties":
                        {"arg1" {"type": "type"} },
                        {"arg2" {"type": "type"} } } }
    """
    if not inspect.isclass(c):
        raise NotAClassException("The parameter %s is not a class" % c)

    def get_methods(c_methods):
        l = []
        for k, v in (c_methods):
            if inspect.ismethod(v):
                l.append(get_method_desc(v))
        return l

    c_name = c.__name__
    if c.__doc__:
        c_docstr = re.sub('"+', '', c.__doc__)
    else:
        c_docstr = "no documentation"
    c_methods = get_methods(inspect.getmembers(c))

    c_desc = '{"id":"%s","description":"%s","type":"object","properties":{' % (c_name, c_docstr)
    for i in c_methods:
        c_desc += i + ',' # adding ',' for the next arg

    c_desc = c_desc[:-1] # removing trailing ','
    c_desc += '}}' # closing the brackets

    return c_desc
