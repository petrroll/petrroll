import pathlib
import re

import dateutil.parser
import feedparser

MAX_TITLE_LEN = 50
BLOG_ENTRIES = 5
README_FILENAME = "README.md"

def shorten_text(text, max_len, placeholder="..."):
    return text if len(text) <= max_len else text[:max_len-len(placeholder)] + placeholder

def build_readme(path):
    entries = fetch_blog_entries()
    entries_md = format_blog_entries(entries)
    
    with path.open("r") as fopen:
        original_readme = fopen.read()
    
    updated_contents = replace_chunk(original_readme, "blog", entries_md)

    with path.open("w") as fopen:
        fopen.write(updated_contents)

def fetch_blog_entries():
    entries = feedparser.parse("https://devblog.petrroll.cz/feed.xml")["entries"]
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
        ["* [{title}]({url}) - _{published}_".format(**entry) for entry in entries[:BLOG_ENTRIES]]
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