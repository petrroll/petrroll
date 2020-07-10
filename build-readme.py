import pathlib
import re

import dateutil.parser
import feedparser

MAX_TITLE_LEN = 60
README_FILENAME = "README.md"
BLOGPOSTS_ENTRIES = 5
BLOGPOSTS_FEED_URL = "https://devblog.petrroll.cz/feed.xml"

def shorten_text(text, max_len, placeholder="..."):
    return text if len(text) <= max_len else text[:max_len-len(placeholder)] + placeholder

def build_readme(path):
    entries = fetch_blog_entries()
    entries_md = format_blog_entries(entries)
    
    with path.open("r") as fopen:
        original_readme = fopen.read()
    
    updated_contents = replace_chunk(original_readme, "blog-posts", entries_md)

    with path.open("w") as fopen:
        fopen.write(updated_contents)

def fetch_blog_entries():
    entries = feedparser.parse(BLOGPOSTS_FEED_URL)["entries"]
    return [
        {
            "title":shorten_text(entry["title"], MAX_TITLE_LEN),
            "url": entry["link"],
            "published": dateutil.parser.parse(entry["published"]).strftime("%b %-d, %Y"),
        }
        for entry in entries
    ]

def format_blog_entries(entries):
    entries_md = "\n".join(
        ["* [{title}]({url}) - _{published}_".format(**entry) for entry in entries[:BLOGPOSTS_ENTRIES]]
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