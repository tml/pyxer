"""Unit Tests for layout templates."""

__revision__ = "$Rev: 421 $"
__author__ = "Daniel Miller <millerdev@nwsdb.com>"
__copyright__ = "Copyright 2006, David Stanek"

import pyxer.kid

def test_layout_error():
    from pyxer.kid.template_util import TemplateLayoutError
    try:
        pyxer.kid.Template("""
            <html xmlns:py="http://purl.org/kid/ns#" py:layout="no_layout" />
            """).serialize()
    except TemplateLayoutError, e:
        e = str(e)
    except Exception:
        e = 'wrong error'
    except:
        e = 'silent'
    assert "'no_layout'" in e
    assert 'not defined' in e
    assert 'while processing layout=' in e

def test_dynamic_layout():
    layout = pyxer.kid.Template("""
        <html xmlns:py="http://purl.org/kid/ns#">
          ${body_content()}
        </html>
        """)
    child = pyxer.kid.Template("""
        <html py:layout="dynamic_layout" xmlns:py="http://purl.org/kid/ns#">
          <body py:def="body_content()">body content</body>
        </html>
        """, dynamic_layout=type(layout))
    output = child.serialize()
    assert output.find("body content") > -1, \
        "body_content function was not executed"

def test_match_locals():
    layout = pyxer.kid.Template("""
        <?python
          test_var = "WRONG VALUE"
        ?>
        <html xmlns:py="http://purl.org/kid/ns#">
          <body>
            <?python
              assert "test_var" in locals(), \
                "test_var is not defined in layout locals"
              assert test_var == "test value", \
                "test_var has wrong value: %r" % test_var
            ?>
            <div />
          </body>
        </html>
        """)
    child = pyxer.kid.Template("""
        <?python
          layout_params["test_var"] = "WRONG VALUE"
        ?>
        <html py:layout="layout" xmlns:py="http://purl.org/kid/ns#">
          <content py:match="item.tag == 'div'" py:strip="True">
            <?python
              assert "test_var" in locals(), \
                "test_var is not defined in py:match locals"
              assert test_var == "test value", \
                "test_var has wrong value in py:match: %r" % test_var
            ?>
            test_var=${test_var}
          </content>
        </html>
        """, layout=type(layout), test_var="test value")
    output = child.serialize()
    assert output.find("test_var=test value") > -1, \
        "match template was not executed"

def test_def_locals():
    layout = pyxer.kid.Template("""
        <?python
          test_var = "WRONG VALUE"
        ?>
        <html xmlns:py="http://purl.org/kid/ns#">
          <body>
            <?python
              assert "test_var" in locals(), \
                "test_var is not defined in layout locals"
              assert test_var == "test value", \
                "test_var has wrong value: %r" % test_var
            ?>
            ${child_content()}
          </body>
        </html>
        """)
    child = pyxer.kid.Template("""
        <?python
          layout_params["test_var"] = "WRONG VALUE"
        ?>
        <html py:layout="layout" xmlns:py="http://purl.org/kid/ns#">
          <content py:def="child_content()" py:strip="True">
            <?python
              assert "test_var" in locals(), \
                "test_var is not defined in py:def locals"
              assert test_var == "test value", \
                "test_var has wrong value in py:def: %r" % test_var
            ?>
            test_var=${test_var}
          </content>
        </html>
        """, layout=type(layout), test_var="test value")
    output = child.serialize()
    assert output.find("test_var=test value") > -1, \
        "child_content function was not executed"
