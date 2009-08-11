"""python 2 json-schema SMD"""

import inspect
import re

try:
    import json
except ImportError:
    import simplejson as json

class NotAClassException(TypeError):
    """raised when the argument is not a class"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class NotAMethodException(TypeError):
    """raised when the argument is not a method"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ConfigurationFileTypeError(TypeError):
    """raised when the configuration file has typeErrors"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SchemaValueError(ValueError):
    """raised when the value to add to the schema is incorrect"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SchemaSealedError(AttributeError):
    """raised when a schema is not allowed to add params"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Py2JSON(object):
    """Py2JSON will handle all the transformations"""

    # this is the type defaults
    types_dict = {"str": "string",
              "int": "integer",
              "bool": "boolean",
              "NoneType": "any",
              "float": "number",
              "classobj": "object",
              "instance": "object",
              "list": "array"}

    # this holds the class (class instance)
    cls = None

    # transport protocol
    transport = "REST"

    # envelope (format)
    envelope = "JSON"

    # target url
    target = None

    # additional parameters
    additional_parameters = True

    # this will be the generated schema
    _schema = {}

    def __init__(self, cls, use_docstrings=False, excluded_methods=[], use_config=True):
        """cls is the class to transform"""
        self._schema = {}
        self.cls = cls

        if use_config:
            # this is trying to load a configuration
            # module that will overwrite defaults
            try:
                import py2json_conf as conf

                # sanity check
                if not isinstance(conf.types_dict, dict):
                    raise ConfigurationFileTypeError("""
                    py2json_config.types_dict is not a dict""")
                elif not isinstance(conf.transport, str):
                    raise ConfigurationFileTypeError("""
                    py2json_config.transport is not a string""")
                elif not isinstance(conf.envelope, str):
                    raise ConfigurationFileTypeError("""
                    py2json_config.envelope is not a string""")
                elif not isinstance(conf.target, str):
                    raise ConfigurationFileTypeError("""
                    py2json_config.target is not a string""")
                elif not isinstance(conf.target, bool):
                    raise ConfigurationFileTypeError("""
                    py2json_config.additionalParameters is not a bool""")
                else:
                    self.types_dict = conf.types_dict
                    self.transport = conf.transport
                    self.envelope = conf.envelope
                    self.target = conf.target
                    self.additional_parameters = conf.additional_parameters
            except ImportError:
                # fail to import confifuration module so we use defaults
                pass

        # now we add the initial params to the schema
        self._schema['transport'] = self.transport
        self._schema['envelope'] = self.envelope
        self._schema['target'] = self.target
        self._schema['additionalParameters'] = self.additional_parameters
        self._get_class_schema(excluded=excluded_methods, docstrings=use_docstrings) # getting services

    @property
    def schema(self):
        """getter _schema in json"""
        return json.dumps(self._schema)

    def to_json_schema_type(self, t):
        """Transform a Python type to a json-schema type"""
        if isinstance(t, type):
            return self.types_dict.get(t.__name__)
        elif isinstance(t, str) and self.types_dict.has_key(t):
            return self.types_dict.get(t)
        else:
            return self.types_dict.get(type(t).__name__)

    def _get_docstring_method(self, name, docstring, optional=False):
        """Get a method from the docstring useful if the class uses outside
           variables not params, the docstring must be restructured text"""
        method_d = {}
        method_d['target'] = name

        tmp_params = {}
        for line in docstring.split('\n'):
            # stay back! I know regular expressions! python!!!
            matches = re.findall(r'(@type|@param)\ (\w+):\ ([A-Za-z_\ ]+)',
                                 line.strip())
            if matches:
                arg_type, arg_name, arg_description = matches[0]
                if not tmp_params.has_key(arg_name):
                    tmp_params[arg_name] = {'name': arg_name}
                    tmp_params[arg_name]['optional'] = optional
                if arg_type == '@param':
                    tmp_params[arg_name]['description'] = arg_description
                elif arg_type == '@type':
                    tmp_params[arg_name]['type'] = self.types_dict[arg_description]

        method_d['parameters'] = tmp_params.values()

        return method_d

    def _get_method_schema(self, m):
        """Get a method dict from a method"""
        if not inspect.ismethod(m):
            raise NotAMethodException("%s is not a method" % m)

        def get_json_schema_args_types(argc, defaults):
            """Convert default names to types and extend the
               defaults to a bigger list"""
            l = []
            if defaults:
                for i in list(defaults):
                    l.append(self.to_json_schema_type(i))
            for i in range(argc - len(l)):
                l.insert(0, self.to_json_schema_type(None))

            return l

        def get_json_schema_args_defaults(argc, defaults):
            """Convert default names to a len(args) list size"""
            l = []
            if defaults:
                for i in list(defaults):
                    l.append(i)
            for i in range(argc - len(l)):
                l.insert(0, None)

            return l

        # final method dict
        m_dict = {} 

        # name used in the target too
        m_dict['target'] = m.__name__ # asign it to target

        # list of params
        m_dict['parameters'] = [] # list of all params

        # inspect the method to get the args and defaults
        args, _, _, defaults = inspect.getargspec(m)

        # some cleaning
        args = args[1:] # removing 'self'

        # if we don't have any arguments, then just close the schema
        if not len(args):
            return m_dict

        # getting all the types
        types = get_json_schema_args_types(len(args), defaults)

        # getting a right defaults array
        defaults = get_json_schema_args_defaults(len(args), defaults)

        m_arguments = zip(args, types, defaults)

        # arg, type, default to add it to the params array
        for _arg, _type, _default in m_arguments:
            val = {}
            if _default == None:
                val = {'name': _arg,
                       'type': _type,
                       'default': _default}
            else:
                val = {'name': _arg,
                       'type': _type,
                       'optional': False,
                       'default': _default}

            m_dict['parameters'].append(val)

        return m_dict

    def _get_class_schema(self, excluded=[], docstrings=False):
        """Get a class dict from a class"""
        if not inspect.isclass(self.cls):
            raise NotAClassException("The parameter %s is not a class" % 
                                      self.cls)

        def get_methods(c_methods):
            """get all the methods for this method descriptor"""
            d = {}
            for key, value in (c_methods):
                if key in excluded:
                    continue
                if inspect.ismethod(value):
                    if docstrings:
                        d_method = self._get_docstring_method(value.__name__, value.__doc__)
                    else:
                        d_method = self._get_method_schema(value)
                    d[d_method['target']] = d_method

            return d

        # getting all the services
        services = get_methods(inspect.getmembers(self.cls))

        # adding services
        self._schema['services'] = services

    def add_param(self, key, value):
        """add a parameter to the schema"""
        if self._schema['additionalParameters'] == False:
            raise SchemaSealedError(
                    "This schema doesn't allow any more params")
        if self._schema.has_key(key):
            raise SchemaValueError(
                    'This schema already has that key, try another one')
        self._schema[key] = value

    def replace_param(self, key, value):
        """replace a schema param"""
        if not self._schema.has_key(key):
            raise SchemaValueError(
                    "This schema doesn't have that key")
        self._schema[key] = value

    def delete_param(self, key):
        """delete a parameter"""
        if not self._schema.has_key(key):
            raise SchemaValueError(
                    "This schema doesn't have that key")
        del self._schema[key]
