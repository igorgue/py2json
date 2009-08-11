from py2json import Py2JSON
import unittest

class Py2JSONTest(unittest.TestCase):
    def test_to_json_schema_type(self):
        """test for to_json_schema_type"""
        class Foo(object):
            def bar(self):
                return 'hello'

        json_smd = Py2JSON(Foo)
        s = 'string'
        assert json_smd.to_json_schema_type(s) == 'string'
        i = 666
        assert json_smd.to_json_schema_type(i) == 'integer'
        f = 666.666
        assert json_smd.to_json_schema_type(f) == 'number'
        l = [6, 6, 6]
        assert json_smd.to_json_schema_type(l) == 'array'
        nill = None
        assert json_smd.to_json_schema_type(nill) == 'any'

    def test_get_docstring_method(self):
        """test for _get_docstring_method"""
        class Foo(object):
            def foo(self):
                """this is the foo method

                   @type param: str
                   @param param: this is the coolest function ever
                """
                print 'bar'
        json_smd = Py2JSON(Foo)
        assert json_smd._get_docstring_method(name='foo', docstring=Foo().foo.__doc__) == {'target': 'foo', 'parameters': [{'type': 'string', 'optional': False, 'name': 'param', 'description': 'this is the coolest function ever'}]}

    def test_get_method_schema(self):
        """test for _get_method_schema"""
        class Foo(object):
            def foo(self, param='this is a string'):
                print 'bar %s' % param

        json_smd = Py2JSON(Foo)
        assert json_smd._get_method_schema(Foo().foo) == {'target': 'foo', 'parameters': [{'default': 'this is a string', 'optional': False, 'type': 'string', 'name': 'param'}]}

    def test_get_class_schema(self):
        """test for _get_class_schema"""
        class Foo(object):
            def bar(self, string="this is a str"):
                print string
            def bar2(self, integer=666):
                print integer

        class Foo2(object):
            "foo description here"
            def bar(self, string="this is a str"):
                print string
            def bar2(self, integer=666):
                print integer

        class Foo3(object):
            "foo description here"
            pass

        json_smd = Py2JSON(Foo)
        assert json_smd.schema == '{"services": {"bar2": {"target": "bar2", "parameters": [{"default": 666, "optional": false, "type": "integer", "name": "integer"}]}, "bar": {"target": "bar", "parameters": [{"default": "this is a str", "optional": false, "type": "string", "name": "string"}]}}, "envelope": "JSON", "target": null, "transport": "REST", "additionalParameters": true}'
        json_smd = Py2JSON(Foo2, excluded_methods=['bar'])
        assert json_smd.schema == '{"services": {"bar2": {"target": "bar2", "parameters": [{"default": 666, "optional": false, "type": "integer", "name": "integer"}]}}, "envelope": "JSON", "target": null, "transport": "REST", "additionalParameters": true}'
        json_smd = Py2JSON(Foo3)
        assert json_smd.schema == '{"services": {}, "envelope": "JSON", "target": null, "transport": "REST", "additionalParameters": true}'

    def test_add_param(self):
        """test for add_param"""
        class Foo(object):
            def bar(self, string="this is a str"):
                print string
            def bar2(self, integer=666):
                print integer
        json_smd = Py2JSON(Foo)
        json_smd.add_param('foo', 12.3)
        assert json_smd.schema == '{"target": null, "envelope": "JSON", "services": {"bar2": {"target": "bar2", "parameters": [{"default": 666, "optional": false, "type": "integer", "name": "integer"}]}, "bar": {"target": "bar", "parameters": [{"default": "this is a str", "optional": false, "type": "string", "name": "string"}]}}, "foo": 12.300000000000001, "transport": "REST", "additionalParameters": true}'

    def test_replace_param(self):
        """test for replace_param"""
        class foo(object):
            def bar(self, string="this is a str"):
                print string
            def bar2(self, integer=666):
                print integer
        json_smd = Py2JSON(foo)
        json_smd.add_param('foo', 12.3)
        json_smd.replace_param('foo', 'py2json replacement')
        assert json_smd.schema == '{"target": null, "envelope": "JSON", "services": {"bar2": {"target": "bar2", "parameters": [{"default": 666, "optional": false, "type": "integer", "name": "integer"}]}, "bar": {"target": "bar", "parameters": [{"default": "this is a str", "optional": false, "type": "string", "name": "string"}]}}, "foo": "py2json replacement", "transport": "REST", "additionalParameters": true}'

    def test_delete_param(self):
        """test for delete param"""
        class Foo(object):
            def bar(self, string="this is a str"):
                print string
            def bar2(self, integer=666):
                print integer
        json_smd = Py2JSON(Foo)
        json_smd.add_param('foo', 12.3)
        json_smd.delete_param('foo')
        assert json_smd.schema == '{"target": null, "envelope": "JSON", "services": {"bar2": {"target": "bar2", "parameters": [{"default": 666, "optional": false, "type": "integer", "name": "integer"}]}, "bar": {"target": "bar", "parameters": [{"default": "this is a str", "optional": false, "type": "string", "name": "string"}]}}, "transport": "REST", "additionalParameters": true}'

if __name__ == '__main__':
    unittest.main()
