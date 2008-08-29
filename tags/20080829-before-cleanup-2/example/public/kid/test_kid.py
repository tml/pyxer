# -*- coding: UTF-8 -*-

master = """\
<html xmlns:py="http://purl.org/kid/ns#">
     <body py:match="item.tag == 'body'">
         <p>my header</p>
         <div py:replace="item[:]" />
         <p>my footer</p>
     </body>
</html>"""

open('master.html', 'w').write(master)

page = """\
<html xmlns:py="http://purl.org/kid/ns#"
         py:extends='load("master.html")'>
     <body>
         <p>my content</p>
     </body>
</html>"""

open('index.html', 'w').write(page)

class KidTemplateManager:

    def __init__(self):
        self.pool = []

    def load(self, path):
        print "Getting", path
        import kid
        # source = open(path, "rb").read()
        template = kid.load_template(
            path, # source,
            cache=False,
            ns=dict(load=self.load))
        self.pool.append(template)
        return template

template = KidTemplateManager().load("index.html")
print template.serialize()
