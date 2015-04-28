# How to find out if you are on a productions system #

If you want to make some features available just in the local testing server you
can use the `stage` indicator e.g.

```
@controller
def testpage():
    if stage:
        return notfound()
   return 'You see me only on the development server'
```

In templates you can do like this:

```
<div py:if='not h.stage'>
You see me only on the development server
</div>
```