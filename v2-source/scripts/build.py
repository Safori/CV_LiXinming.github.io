#!/usr/bin/env python3
"""Build deterministic static HTML from content JSON. Python 3 standard library only."""
import json
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=lambda value:escape(str(value),quote=True)
LINKS=[("Prof. Xiao Gong","https://cde.nus.edu.sg/ece/staff/gong-xiao/"),("Prof. Yuan Li","https://faculty.sdu.edu.cn/liyuan/en/index.htm"),("National University of Singapore","https://www.nus.edu.sg"),("Shandong University","https://www.sdu.edu.cn")]
def linkify(text):
    for phrase,url in LINKS:
        text=text.replace(E(phrase),f'<a href="{url}">{E(phrase)}</a>')
    return text
def load(name): return json.loads((ROOT/'content'/name).read_text(encoding='utf-8'))
def render():
    site=load('site.json'); pubs=load('publications.json')
    education=''.join(f'<div class="education-item"><span class="period">{E(x["period"])}</span><div><h3>{linkify(E(x["institution"]))}</h3><p>{E(x["degree"])}</p><p class="muted">Advisor: {linkify(E(x["advisor"]))}</p></div></div>' for x in site['education'])
    def news_item(x):
        photo=f'<details><summary>View conference photo</summary><figure><img src="{E(x["image"])}" loading="lazy" alt="{E(x["caption"])}" width="1280" height="960"><figcaption>{E(x["caption"])}</figcaption></figure></details>' if x.get("image") else ''
        return f'<div class="news-item"><time datetime="{E(x["date"])}">{E(x["display_date"])}</time><div><p>{E(x["text"])}</p>{photo}</div></div>'
    news=''.join(news_item(x) for x in site['news'])
    articles=[];cvpubs=[]
    for p in sorted(pubs,key=lambda p:-p['year']):
        # P0 fix: exact-name match is only for highlighting, never for control flow.
        # A variant/missing name must not crash the whole build.
        try: mi=p['authors'].index(site['name'])
        except ValueError: mi=-1
        names=', '.join('<strong class="author-me">'+E(a)+'</strong>' if a==site['name'] else E(a) for a in p['authors'])
        # Expose complete authors without making every publication visually dense.
        shown=max(3,mi+1) if mi>=0 else 3
        short=', '.join(p['authors'][:shown])
        if len(p['authors'])>shown:short+=', et al.'
        if mi>=0 and mi<shown:short=E(short).replace(E(site['name']),'<strong class="author-me">'+E(site['name'])+'</strong>')
        else:short=E(short)
        citation=', '.join(p['authors'])+'. “'+p['title']+'.” '+p['venue']+', '+str(p['year'])+'. '+p['url']
        search=E(' '.join([p['title'],' '.join(p['authors']),str(p['year']),p['venue'],p.get('short_venue',''),p.get('type',''),p.get('summary','')]).lower())
        summary=f'<p class="paper-summary">{E(p["summary"])}</p>' if p.get('summary') else ''
        badge='<span class="cofirst">Co-first author</span>' if p['co_first'] else ''
        articles.append(f'''<article class="paper" data-kind="{E(p['type'])}" data-search="{search}"><div class="paper-meta"><span>{p['year']}</span><span>{E(p['short_venue'])}</span></div><div><h3><a href="{E(p['url'])}">{E(p['title'])}</a></h3><p>{short}</p><p class="venue">{E(p['venue'])}{badge}</p>{summary}<div class="paper-actions"><a href="{E(p['url'])}">Publisher</a><button class="copy-citation" data-citation="{E(citation)}" hidden>Copy citation</button><details class="authors-details"><summary>All authors</summary><p>{names}</p></details></div></div></article>''')
        cvpubs.append(f'<article class="cv-paper"><h3><a href="{E(p["url"])}">{E(p["title"])}</a></h3><p>{names}</p><p class="muted">{E(p["venue"])}, {p["year"]}{" · Co-first author" if p["co_first"] else ""}</p></article>')
    values={k:E(v) for k,v in site.items() if isinstance(v,str)}
    values['institution']=linkify(values['institution'])
    values.update(biography=''.join('<p>'+linkify(E(p))+'</p>' for p in site['biography']),interests=''.join('<li>'+E(i)+'</li>' for i in site['interests']),news=news,education=education,publications=''.join(articles))
    result=(ROOT/'templates/index.html').read_text()
    for k,v in values.items():result=result.replace('{{'+k+'}}',v)
    (ROOT/'dist/index.html').write_text(result,encoding='utf-8')
    cv=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{E(site['name'])}, PhD student at the National University of Singapore. Research in semiconductor devices and ferroelectric memory."><meta property="og:title" content="{E(site['name'])} | Curriculum Vitae"><meta property="og:description" content="{E(site['name'])}, PhD student at the National University of Singapore."><meta property="og:type" content="profile"><meta property="og:url" content="https://safori.github.io/CV_LiXinming.github.io/cv.html"><meta property="og:image" content="assets/og-image.jpg"><meta name="twitter:card" content="summary_large_image"><title>{E(site['name'])} | Curriculum Vitae</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="cv.js" defer></script></head><body><main class="container cv"><div class="cv-toolbar"><a href="index.html">Back to website</a><button id="print-cv" hidden>Print / Save as PDF</button></div><h1>{E(site['name'])} <span lang="zh">{E(site['chinese_name'])}</span></h1><p>{E(site['position'])}<br>{linkify(E(site['institution']))}<br><a href="mailto:{E(site['email'])}">{E(site['email'])}</a></p><section class="section"><h2>Education</h2>{education}</section><section class="section"><h2>Research interests</h2><ul class="interests">{values['interests']}</ul></section><section class="section"><h2>Selected publications</h2>{''.join(cvpubs)}</section><p class="cv-note muted">Publication details reproduced from the public CV. This page is a selected academic profile, not a complete publication record.</p></main></body></html>'''
    (ROOT/'dist/cv.html').write_text(cv,encoding='utf-8')
if __name__=='__main__':render();print('Built index.html and cv.html')
