#!/usr/bin/env python3
"""Build deterministic static HTML from content JSON. Python 3 standard library only.

Generates a multi-page site: index, research, publications, talks, news, cv.
All content comes from content/*.json; nothing is invented at build time.
"""
import json
import re
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=lambda value:escape(str(value),quote=True)
LINKS=[("Prof. Xiao Gong","https://cde.nus.edu.sg/ece/staff/gong-xiao/"),("Prof. Yuan Li","https://faculty.sdu.edu.cn/liyuan/en/index.htm"),("National University of Singapore","https://www.nus.edu.sg"),("Shandong University","https://www.sdu.edu.cn")]
def linkify(text):
    for phrase,url in LINKS:
        text=text.replace(E(phrase),f'<a href="{url}">{E(phrase)}</a>')
    return text
def md_inline(text):
    """Escape, then convert **bold** spans (used in blog posts)."""
    out=E(text)
    out=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',out)
    return out
def load(name): return json.loads((ROOT/'content'/name).read_text(encoding='utf-8'))
NAV=[("index.html","Home"),("research.html","Research"),("publications.html","Publications"),("talks.html","Talks"),("news.html","News"),("cv.html","CV")]
def nav(active):
    items=''.join(f'<a href="{href}"{" aria-current=\"page\"" if href==active else ""}>{label}</a>' for href,label in NAV)
    return f'<nav aria-label="Main navigation">{items}</nav>'
def fill(template, values):
    result=(ROOT/'templates'/template).read_text(encoding='utf-8')
    for k,v in values.items():result=result.replace('{{'+k+'}}',v)
    return result
def short_authors(p, site):
    # P0 fix: exact-name match is only for highlighting, never for control flow.
    try: mi=p['authors'].index(site['name'])
    except ValueError: mi=-1
    shown=max(3,mi+1) if mi>=0 else 3
    short=', '.join(p['authors'][:shown])
    if len(p['authors'])>shown:short+=', et al.'
    if mi>=0 and mi<shown:short=E(short).replace(E(site['name']),'<strong class="author-me">'+E(site['name'])+'</strong>')
    else:short=E(short)
    return short
def full_authors(p, site):
    return ', '.join('<strong class="author-me">'+E(a)+'</strong>' if a==site['name'] else E(a) for a in p['authors'])
def article(p, site, copy_button):
    short=short_authors(p, site)
    names=full_authors(p, site)
    citation=', '.join(p['authors'])+'. "'+p['title']+'." '+p['venue']+', '+str(p['year'])+'. '+p['url']
    search=E(' '.join([p['title'],' '.join(p['authors']),str(p['year']),p['venue'],p.get('short_venue',''),p.get('type',''),p.get('summary','')]).lower())
    badge='<span class="cofirst">Co-first author</span>' if p['co_first'] else ''
    summary=f'<p class="paper-summary">{E(p["summary"])}</p>' if p.get('summary') else ''
    copy=f'<button class="copy-citation" data-citation="{E(citation)}" hidden>Copy citation</button>' if copy_button else ''
    return f'''<article class="paper" data-kind="{E(p['type'])}" data-search="{search}"><div class="paper-meta"><span>{p['year']}</span><span>{E(p['short_venue'])}</span></div><div><h3><a href="{E(p['url'])}">{E(p['title'])}</a></h3><p>{short}</p><p class="venue">{E(p['venue'])}{badge}</p>{summary}<div class="paper-actions"><a href="{E(p['url'])}">Publisher</a>{copy}<details class="authors-details"><summary>All authors</summary><p>{names}</p></details></div></div></article>'''
def news_item(x):
    photo=f'<details><summary>View conference photo</summary><figure><img src="{E(x["image"])}" loading="lazy" alt="{E(x["caption"])}" width="1280" height="960"><figcaption>{E(x["caption"])}</figcaption></figure></details>' if x.get("image") else ''
    return f'<div class="news-item"><time datetime="{E(x["date"])}">{E(x["display_date"])}</time><div><p>{E(x["text"])}</p>{photo}</div></div>'
def render():
    site=load('site.json'); pubs=load('publications.json'); research=load('research.json')
    talks=load('talks.json'); posts=load('posts.json'); accepted=load('accepted.json')
    pubs_sorted=sorted(pubs,key=lambda p:-p['year'])
    by_id={p['id']:p for p in pubs}
    education=''.join(f'<div class="education-item"><span class="period">{E(x["period"])}</span><div><h3>{linkify(E(x["institution"]))}</h3><p>{E(x["degree"])}</p><p class="muted">Advisor: {linkify(E(x["advisor"]))}</p></div></div>' for x in site['education'])
    news=''.join(news_item(x) for x in site['news'])
    values={k:E(v) for k,v in site.items() if isinstance(v,str)}
    values['institution']=linkify(values['institution'])
    values.update(biography=''.join('<p>'+linkify(E(p))+'</p>' for p in site['biography']),
                  biography_zh=linkify(E(site['biography_zh'])),
                  interests=''.join('<li>'+E(i)+'</li>' for i in site['interests']),
                  news=news, education=education)
    # --- Home ---
    stats=''.join(f'<div class="stat"><b>{b}</b><span>{s}</span></div>' for b,s in [
        ('6','peer-reviewed papers, 2024–2026'),('2','first-author papers'),
        ('2× VLSI · 2× IEDM','top conference papers'),('1','paper accepted at IEDM 2026')])
    values.update(nav=nav('index.html'), stats=stats,
                  selected_publications=''.join(article(p,site,False) for p in pubs_sorted[:3]))
    (ROOT/'dist/index.html').write_text(fill('index.html',values),encoding='utf-8')
    # --- Research ---
    themes=[]
    for t in research:
        links=[]
        for pid in t['papers']:
            p=by_id[pid]; links.append(f'<a href="{E(p["url"])}">{E(p["title"])}</a>')
        if t.get('accepted'):
            links.append(f'<a href="publications.html">{E(accepted["title"])}</a> (accepted, IEDM 2026)')
        link_html='<p class="theme-links">Related work:<br>'+'<br>'.join(links)+'</p>' if links else ''
        themes.append(f'<section class="section theme"><h2>{E(t["title"])}</h2><p>{E(t["description"])}</p>{link_html}</section>')
    (ROOT/'dist/research.html').write_text(fill('research.html',{**values,'nav':nav('research.html'),'themes':''.join(themes)}),encoding='utf-8')
    # --- Publications (full list + accepted) ---
    acc_names=full_authors(accepted,site)
    acc_badge='<span class="cofirst">Co-first author</span>' if accepted['co_first'] else ''
    accepted_html=f'''<article class="paper"><div class="paper-meta"><span>{accepted['year']}</span><span>IEDM</span></div><div><h3>{E(accepted['title'])}</h3><p>{short_authors(accepted,site)}</p><p class="venue">{E(accepted['venue'])}{acc_badge}</p><p class="paper-summary">{E(accepted['summary'])}</p><p class="muted">{E(accepted['status'])}</p><div class="paper-actions"><details class="authors-details"><summary>All authors</summary><p>{acc_names}</p></details></div></div></article>'''
    (ROOT/'dist/publications.html').write_text(fill('publications.html',{**values,'nav':nav('publications.html'),
        'accepted':accepted_html,
        'publications':''.join(article(p,site,True) for p in pubs_sorted)}),encoding='utf-8')
    # --- Talks ---
    talk_items=[]
    for t in talks:
        badge='<span class="badge">Upcoming</span>' if t['status']=='upcoming' else ''
        link=''
        if t.get('paper_id'):
            p=by_id[t['paper_id']]; link=f' <a href="{E(p["url"])}">Paper</a>'
        talk_items.append(f'''<section class="section talk"><time datetime="{E(t['date'])}">{E(t['display_date'])}</time><h2>{E(t['title'])}{badge}</h2><p>{E(t['event'])} · {E(t['location'])}</p><p class="muted">{E(t['note'])}{link}</p></section>''')
    (ROOT/'dist/talks.html').write_text(fill('talks.html',{**values,'nav':nav('talks.html'),'talks':''.join(talk_items)}),encoding='utf-8')
    # --- News & blog ---
    post_items=[]
    for post in posts:
        body=''
        for b in post['blocks']:
            if 'h' in b: body+=f'<h3>{E(b["h"])}</h3>'
            else: body+=f'<p>{md_inline(b["p"])}</p>'
        photos=''
        if post.get('images'):
            imgs=''.join(f'<img src="{E(i)}" loading="lazy" alt="VLSI 2026 photo">' for i in post['images'])
            photos=f'<div class="post-photos">{imgs}</div>'
        post_items.append(f'''<article class="post"><time datetime="{E(post['date'])}">{E(post['display_date'])}</time><h3>{E(post['title'])}</h3>{body}{photos}</article>''')
    (ROOT/'dist/news.html').write_text(fill('news.html',{**values,'nav':nav('news.html'),'posts':''.join(post_items)}),encoding='utf-8')
    # --- CV (same content, with site nav) ---
    cvpubs=[]
    for p in pubs_sorted:
        cvpubs.append(f'<article class="cv-paper"><h3><a href="{E(p["url"])}">{E(p["title"])}</a></h3><p>{full_authors(p,site)}</p><p class="muted">{E(p["venue"])}, {p["year"]}{" · Co-first author" if p["co_first"] else ""}</p></article>')
    cv=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{E(site['name'])}, PhD student at the National University of Singapore. Research in semiconductor devices and ferroelectric memory."><meta property="og:title" content="{E(site['name'])} | Curriculum Vitae"><meta property="og:description" content="{E(site['name'])}, PhD student at the National University of Singapore."><meta property="og:type" content="profile"><meta property="og:url" content="https://safori.github.io/CV_LiXinming.github.io/cv.html"><meta property="og:image" content="assets/og-image.jpg"><meta name="twitter:card" content="summary_large_image"><title>{E(site['name'])} | Curriculum Vitae</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="cv.js" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header class="header container"><a class="brand" href="index.html">{E(site['name'])}</a>{nav('cv.html')}</header><main id="main" class="container cv"><div class="cv-toolbar"><a href="index.html">Back to website</a><button id="print-cv" hidden>Print / Save as PDF</button></div><h1>{E(site['name'])} <span lang="zh">{E(site['chinese_name'])}</span></h1><p>{E(site['position'])}<br>{linkify(E(site['institution']))}<br><a href="mailto:{E(site['email'])}">{E(site['email'])}</a></p><section class="section"><h2>Education</h2>{education}</section><section class="section"><h2>Research interests</h2><ul class="interests">{values['interests']}</ul></section><section class="section"><h2>Selected publications</h2>{''.join(cvpubs)}</section><p class="cv-note muted">Publication details reproduced from the public CV. This page is a selected academic profile, not a complete publication record.</p></main><footer class="container"><span>© 2026 {E(site['name'])}</span><a href="cv.html">Back to top</a></footer></body></html>'''
    (ROOT/'dist/cv.html').write_text(cv,encoding='utf-8')
    print('Built index, research, publications, talks, news, cv')
if __name__=='__main__':render()
