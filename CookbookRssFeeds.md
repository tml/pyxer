# RSS Feeds #

The most simple way to add RSS Feeds is to use an XML template like this:

```
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>
            XXX
        </title>
        <link>
            http://www.example.com/rss
        </link>
        <atom:link type="application/rss+xml" rel="self" href="http://www.example.com/rss"/>
        <description>
           XXX
        </description>
        <language>
            en-us
        </language>
        <ttl>
            40
        </ttl>
        <item py:for="m in c.messages">
            <title py:content='m.text'>
               Titel 
            </title>
            <description py:content='m.text'>
                Description
            </description>
            <pubDate py:content='m.created'>
                Tue, 26 May 2009 17:00:39 +0000
            </pubDate>
            <guid py:content='m.url'>
                http://example.com/xxx
            </guid>
            <link py:content='m.url'>
                http://example.com/xxx
            </link>
        </item>
    </channel>
</rss>
```

The corresponding controller function looks like this:

```
@controller(template="feed.xml", method="xml", encoding="utf8")
def rss():    
    c.messages = Messages.all().fetch(40)
```