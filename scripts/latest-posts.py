"""Replace the block between the posts markers in README.md with the newest gatezh.com posts.

Reads the site's RSS feed and keeps only /posts/ entries (the feed also carries
Ever Learning notes on other people's articles). Standard library only.
"""
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEED = "https://gatezh.com/index.xml"
COUNT = 3
START, END = "<!-- posts:start -->", "<!-- posts:end -->"

readme = Path(sys.argv[1] if len(sys.argv) > 1 else "README.md")
request = urllib.request.Request(FEED, headers={"User-Agent": "gatezh-profile-readme"})
with urllib.request.urlopen(request, timeout=30) as response:
    channel = ET.fromstring(response.read()).find("channel")

lines = []
for item in channel.findall("item"):
    link = item.findtext("link", "")
    if "/posts/" not in link:
        continue
    date = parsedate_to_datetime(item.findtext("pubDate")).strftime("%b %Y")
    lines.append(f"- [{item.findtext('title')}]({link}) · {date}")
    if len(lines) == COUNT:
        break

if not lines:
    sys.exit("no posts found in the feed; leaving README.md unchanged")

text = readme.read_text()
head, rest = text.split(START, 1)
_, tail = rest.split(END, 1)
readme.write_text(f"{head}{START}\n" + "\n".join(lines) + f"\n{END}{tail}")
