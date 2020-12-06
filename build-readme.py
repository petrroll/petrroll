import pathlib
import re

import dateutil.parser
import feedparser
import re

README_FILENAME = "README.md"

BLOGPOST_MAX_TITLE_LEN = 90
BLOGPOSTS_ENTRIES = 6
BLOGPOSTS_FEED_URL = "https://devblog.petrroll.cz/feed.xml"

TIL_MAX_TITLE_LEN = 60
TIL_ENTRIES = 4
TIL_FEED_URL = "https://devblog.petrroll.cz/feed/til.xml"


def shorten_text(text, max_len, placeholder="..."):
    return text if len(text) <= max_len else text[:max_len-len(placeholder)] + placeholder

def build_readme(path):
    entries_blog = fetch_blog_entries()
    entries_blog_md = format_entries_to_md(entries_blog, BLOGPOSTS_ENTRIES)

    entries_til = fetch_til_entries()
    entries_til_md = format_entries_to_md(entries_til, TIL_ENTRIES)
    
    with path.open("r") as fopen:
        original_readme = fopen.read()
    
    updated_contents = replace_chunk(original_readme, "blog-posts", entries_blog_md)
    updated_contents = replace_chunk(updated_contents, "tils-posts", entries_til_md)

    with path.open("w") as fopen:
        fopen.write(updated_contents)

def fetch_til_entries():
    entries = feedparser.parse(TIL_FEED_URL)["entries"]
    ahref_reg = re.compile('href=\"(?P<URL>.*)\">(?P<TITLE>.*)</a>') # This isn't robust but since I control the a-href generation (jekyll, templated TIL entry) it's relatively safe

    res = [
        {
            "title":shorten_text(title, TIL_MAX_TITLE_LEN),
            "url": url,
            "published": published,
        }
        for (published, (url, title)) in map(
            lambda x: (
                dateutil.parser.parse(x["published"]).strftime("%b %-d, %Y"),
                ahref_reg.search(x["summary"]).group("URL", "TITLE")
            ),
            entries
        )
    ]
    return res

def fetch_blog_entries():
    entries = feedparser.parse(BLOGPOSTS_FEED_URL)["entries"]
    return [
        {
            "title":shorten_text(entry["title"], BLOGPOST_MAX_TITLE_LEN),
            "url": entry["link"],
            "published": dateutil.parser.parse(entry["published"]).strftime("%b %-d, %Y"),
        }
        for entry in entries
    ]

def format_entries_to_md(entries, max_entries):
    entries_md = "\n".join(
        ["* [{title}]({url}) - _{published}_".format(**entry) for entry in entries[:max_entries]]
    )

    return entries_md

def replace_chunk(content, marker, chunk):
    r = re.compile(
        rf"<!\-\- {marker} starts \-\->.*<!\-\- {marker} ends \-\->",
        re.DOTALL,
    )
    chunk = f"<!-- {marker} starts -->\n{chunk}\n<!-- {marker} ends -->"
    return r.sub(chunk, content)

if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.resolve()
    readme = root / README_FILENAME

    build_readme(readme)