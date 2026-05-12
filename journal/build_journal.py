#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from html import escape
from datetime import datetime
import re

BASE_DIR = Path("/Users/ccc/Documents/personal-website")
ARTICLE_DIR = BASE_DIR / "journal"

TXT_DIR = ARTICLE_DIR

INDEX_HTML = BASE_DIR / "index.html"
JOURNAL_HTML = BASE_DIR / "journal.html"

SITE_NAME_CN = "曹程驰"
SITE_NAME_EN = "Chengchi Cao"
FOOTER_TEXT = "© 2026 Chengchi Cao"


def clean_filename(name):
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name or "untitled"


def split_paragraphs(text):
    paras = re.split(r"\n\s*\n", text.strip())
    return [p.strip().replace("\n", " ") for p in paras if p.strip()]


def get_field(block, zh_key, en_key):
    pattern = rf"^(?:{re.escape(zh_key)}：|{re.escape(en_key)}:)\s*(.*)$"
    m = re.search(pattern, block, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_body(block, zh=True):
    key = "正文：" if zh else "Body:"
    idx = block.find(key)
    if idx == -1:
        return ""
    return block[idx + len(key):].strip()


def parse_date_for_sort(date_text):
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_text)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    for fmt in ["%B %d, %Y", "%b %d, %Y"]:
        try:
            date_part = date_text.split("·")[0].strip()
            return datetime.strptime(date_part, fmt)
        except ValueError:
            pass

    return datetime.min


def parse_txt(path):
    text = path.read_text(encoding="utf-8")

    zh_match = re.search(r"\[中文\](.*?)(?=\[English\]|\Z)", text, re.S)
    en_match = re.search(r"\[English\](.*)", text, re.S)

    zh_block = zh_match.group(1).strip() if zh_match else ""
    en_block = en_match.group(1).strip() if en_match else ""

    zh_title = get_field(zh_block, "标题", "Title")
    zh_date = get_field(zh_block, "日期", "Date")
    filename = get_field(zh_block, "文件名", "Filename")
    zh_summary = get_field(zh_block, "摘要", "Summary")
    zh_body = get_body(zh_block, zh=True)

    en_title = get_field(en_block, "标题", "Title")
    en_date = get_field(en_block, "日期", "Date")
    en_summary = get_field(en_block, "摘要", "Summary")
    en_body = get_body(en_block, zh=False)

    if not filename:
        filename = zh_title or path.stem

    return {
        "source": path,
        "filename": clean_filename(filename),
        "sort_date": parse_date_for_sort(zh_date or en_date),
        "zh": {
            "title": zh_title or path.stem,
            "date": zh_date,
            "summary": zh_summary,
            "body": split_paragraphs(zh_body),
        },
        "en": {
            "title": en_title or zh_title or path.stem,
            "date": en_date or zh_date,
            "summary": en_summary or zh_summary,
            "body": split_paragraphs(en_body) or split_paragraphs(zh_body),
        },
    }


def build_article_html(entry):
    zh = entry["zh"]
    en = entry["en"]

    paras = []
    max_len = max(len(zh["body"]), len(en["body"]))

    for i in range(max_len):
        zh_text = zh["body"][i] if i < len(zh["body"]) else ""
        en_text = en["body"][i] if i < len(en["body"]) else zh_text

        paras.append(f'''      <p
        data-i18n="journalEntryBody{i + 1}"
        data-zh="{escape(zh_text, quote=True)}"
        data-en="{escape(en_text, quote=True)}"
      >
        {escape(zh_text)}
      </p>''')

    paras_html = "\n".join(paras)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(zh["title"])} | {SITE_NAME_CN}</title>
  <link rel="stylesheet" href="../style.css" />
</head>
<body>
  <div class="site-shell">
    <header class="site-header">
      <a class="brand" href="../index.html">
        <span class="brand-cn">{SITE_NAME_CN}</span>
        <span class="brand-en">{SITE_NAME_EN}</span>
      </a>
      <nav class="site-nav">
        <a href="../index.html" data-i18n="navHome" data-zh="首页" data-en="Home">首页</a>
        <a href="../about.html" data-i18n="navAbout" data-zh="简介" data-en="About">简介</a>
        <a href="../journal.html" class="is-active" data-i18n="navJournal" data-zh="随笔" data-en="Journal">随笔</a>
        <a href="../photography.html" data-i18n="navPhotography" data-zh="摄影" data-en="Photography">摄影</a>
        <a href="../research.html" data-i18n="navResearch" data-zh="研究" data-en="Research">研究</a>
        <a href="../contact.html" data-i18n="navContact" data-zh="联系" data-en="Contact">联系</a>
      </nav>
      <button class="lang-toggle" id="lang-toggle" type="button" aria-label="切换语言">EN</button>
    </header>

    <main class="article-shell">
      <a class="back-link" href="../journal.html" data-i18n="backToJournal" data-zh="返回随笔列表" data-en="Back to Journal">返回随笔列表</a>

      <p class="journal-meta"
        data-i18n="journalMeta"
        data-zh="{escape(zh["date"], quote=True)}"
        data-en="{escape(en["date"], quote=True)}"
      >
        {escape(zh["date"])}
      </p>

      <h1
        data-i18n="journalEntryTitle"
        data-zh="{escape(zh["title"], quote=True)}"
        data-en="{escape(en["title"], quote=True)}"
      >
        {escape(zh["title"])}
      </h1>

{paras_html}
    </main>

    <footer class="site-footer">{FOOTER_TEXT}</footer>
  </div>
  <script src="../script.js"></script>
</body>
</html>
'''


def make_post_card(entry, i):
    zh = entry["zh"]
    en = entry["en"]
    href = f"journal/{entry['filename']}.html"
    key = f"Auto{i}"

    return f'''          <article class="post-card">
            <p class="journal-meta" data-i18n="journalMeta{key}" data-zh="{escape(zh["date"], quote=True)}" data-en="{escape(en["date"], quote=True)}">{escape(zh["date"])}</p>
            <h3 data-i18n="journalEntryTitle{key}" data-zh="{escape(zh["title"], quote=True)}" data-en="{escape(en["title"], quote=True)}">{escape(zh["title"])}</h3>
            <p
              data-i18n="journalExcerpt{key}"
              data-zh="{escape(zh["summary"], quote=True)}"
              data-en="{escape(en["summary"], quote=True)}"
            >
              {escape(zh["summary"])}
            </p>
            <a class="text-link" href="{href}" data-i18n="readPost" data-zh="阅读全文" data-en="Read Full Post">阅读全文</a>
          </article>'''


def make_feature_entry(entry):
    zh = entry["zh"]
    en = entry["en"]
    href = f"journal/{entry['filename']}.html"

    return f'''        <article class="feature-entry">
          <p class="journal-meta" data-i18n="journalMetaLatest" data-zh="{escape(zh["date"], quote=True)}" data-en="{escape(en["date"], quote=True)}">{escape(zh["date"])}</p>
          <h3 data-i18n="journalEntryTitleLatest" data-zh="{escape(zh["title"], quote=True)}" data-en="{escape(en["title"], quote=True)}">{escape(zh["title"])}</h3>
          <p
            data-i18n="journalExcerptLatest"
            data-zh="{escape(zh["summary"], quote=True)}"
            data-en="{escape(en["summary"], quote=True)}"
          >
            {escape(zh["summary"])}
          </p>
          <a class="text-link" href="{href}" data-i18n="readPost" data-zh="阅读全文" data-en="Read Full Post">阅读全文</a>
        </article>'''


def replace_between(text, start_pattern, end_pattern, replacement):
    pattern = re.compile(start_pattern + r".*?" + end_pattern, re.S)
    m = pattern.search(text)
    if not m:
        raise RuntimeError("Could not find target block in HTML.")
    return text[:m.start()] + replacement + text[m.end():]


def update_journal_page(entries):
    html = JOURNAL_HTML.read_text(encoding="utf-8")
    cards = "\n\n".join(make_post_card(e, i + 1) for i, e in enumerate(entries))

    new_post_list = f'''<div class="post-list">

{cards}
        </div>'''

    html = replace_between(
        html,
        r'<div class="post-list">',
        r'</div>\s*</section>',
        new_post_list + "\n      </section>"
    )

    JOURNAL_HTML.write_text(html, encoding="utf-8")


def update_index_page(entries):
    if not entries:
        return

    latest = entries[0]
    html = INDEX_HTML.read_text(encoding="utf-8")
    feature = make_feature_entry(latest)

    html = replace_between(
        html,
        r'<article class="feature-entry">',
        r'</article>\s*</section>',
        feature + "\n      </section>"
    )

    INDEX_HTML.write_text(html, encoding="utf-8")


def main():
    ARTICLE_DIR.mkdir(exist_ok=True)

    txt_files = sorted(TXT_DIR.glob("*.txt"))

    entries = []
    for path in txt_files:
        entry = parse_txt(path)
        entries.append(entry)

    entries.sort(key=lambda x: x["sort_date"], reverse=True)

    for entry in entries:
        out_path = ARTICLE_DIR / f"{entry['filename']}.html"
        out_path.write_text(build_article_html(entry), encoding="utf-8")
        print(f"Generated article: {out_path}")

    update_journal_page(entries)
    print(f"Updated: {JOURNAL_HTML}")

    update_index_page(entries)
    print(f"Updated: {INDEX_HTML}")

    print(f"\nDone. Generated {len(entries)} journal articles.")


if __name__ == "__main__":
    main()
