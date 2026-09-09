#!/usr/bin/env python3
from __future__ import annotations
import argparse
import math
import os
import re
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence
from PIL import Image, ImageDraw, ImageFont

BRIEF: dict[str, Any] = {
    "date": "2026-09-09",
    "layout": "single",
    "slide_count": 1,
    "thesis": "Developer AI is becoming an operating layer.",
    "accent_phrase": "becoming an operating layer",
    "read_through": (
        "Teams now need to evaluate the systems around an agent, not only "
        "the model itself. Orchestration, access boundaries, visibility and "
        "failure handling are becoming part of the buying decision."
    ),
    "items": [
        {
            "name": "Pydantic AI Harness",
            "version": "0.30.0",
            "release_date": "2026-09-08",
            "licence": "MIT",
            "platform": "Python 3.10+; OS matrix not stated",
            "repo_url": "https://github.com/pydantic/pydantic-ai-harness",
        },
        {
            "name": "GitHub Copilot CLI",
            "version": "1.0.84-2",
            "release_date": "2026-09-08",
            "licence": "GitHub Copilot CLI License",
            "platform": "Windows, macOS, Linux",
            "repo_url": "https://github.com/github/copilot-cli",
        },
        {
            "name": "Hermes Agent",
            "version": "0.21.1",
            "release_date": "2026-09-07",
            "licence": "MIT",
            "platform": "Windows 10/11, macOS, Linux",
            "repo_url": "https://github.com/NousResearch/hermes-agent",
        },
    ],
    "footer_sources": [
        "Pydantic AI Harness — 8 Sep 2026 — https://github.com/pydantic/pydantic-ai-harness/releases/tag/v0.30.0",
        "GitHub Copilot CLI — 8 Sep 2026 — https://github.com/github/copilot-cli/releases/tag/v1.0.84-2",
        "Hermes Agent — 7 Sep 2026 — https://github.com/NousResearch/hermes-agent/releases/tag/v0.21.1",
    ],
}

WIDTH = 1080
HEIGHT = 1350
MAX_RENDER_Y = 1278
MARGIN_X = 72
LEFT_X = 72
LEFT_W = 540
GUTTER = 36
RIGHT_X = LEFT_X + LEFT_W + GUTTER
RIGHT_W = 360
CONTENT_TOP = 355
FOOTER_DIVIDER_Y = 1030
AVAILABLE_CONTENT_HEIGHT = FOOTER_DIVIDER_Y - CONTENT_TOP
MIN_VERTICAL_SPACING = 24.0
MAX_VERTICAL_SPACING = 160.0
LOGO_X = 72
LOGO_Y = 52
LOGO_W = 190
DATE_RIGHT = WIDTH - 72
DATE_Y = 66
EYEBROW_X = 72
EYEBROW_Y = 136
SINGLE_THESIS_X = 72
SINGLE_THESIS_Y = 185
SINGLE_THESIS_W = WIDTH - 144
HEADER_CONTENT_LIMIT = CONTENT_TOP - 24
FOOTER_TOP = FOOTER_DIVIDER_Y + 20
FOOTER_META_X = LEFT_X
FOOTER_META_W = LEFT_W
FOOTER_SOURCE_X = RIGHT_X
FOOTER_SOURCE_W = RIGHT_W
FOOTER_TEXT_TOP = FOOTER_TOP + 28
FOOTER_TEXT_MAX_Y = 1238
PAGE_NUMBER_Y = 1252
CARD_RADIUS = 20
PANEL_RADIUS = 24
ITEM_PAD_X = 20
ITEM_PAD_Y = 20
ITEM_NUMBER_W = 52
ITEM_TEXT_GAP = 8
PANEL_PAD_X = 26
PANEL_PAD_Y = 24
MIN_PANEL_CLEARANCE = 12.0
BG = (3, 7, 17)
PANEL = (17, 26, 43)
CARD = (12, 19, 32)
CARD_ALT = (14, 22, 37)
TEXT = (248, 250, 252)
MUTED = (148, 163, 184)
FAINT = (100, 116, 139)
ACCENT = (245, 158, 11)
DIVIDER = (45, 57, 76)
FONT_SIZE = {"eyebrow":14,"date":15,"thesis":54,"carousel_title":38,"item_name":24,"item_number":15,"item_meta":15,"panel_label":13,"read_through":24,"carousel_thesis":38,"index_item":20,"footer_label":11,"footer":12,"page":11}
TRACKING = {"eyebrow":1.8,"date":0.6,"thesis":-0.8,"carousel_title":-0.4,"item_name":-0.25,"panel_label":1.5,"footer_label":1.25}
FONT_CANDIDATES = {"display_bold":["InterDisplay-Bold.otf","InterDisplay-Bold.ttf"],"display_semibold":["InterDisplay-SemiBold.otf","InterDisplay-SemiBold.ttf"],"regular":["Inter-Regular.otf","Inter-Regular.ttf"],"semibold":["Inter-SemiBold.otf","Inter-SemiBold.ttf"]}
class RenderError(RuntimeError): pass

def font_search_roots():
    roots=[]
    try: roots.append(Path(__file__).resolve().parent)
    except NameError: pass
    roots += [Path.cwd(),Path('/mnt/data'),Path('/usr/share/fonts'),Path('/usr/local/share/fonts'),Path('/home/oai/share'),Path('/home/oai/.fonts'),Path.home()/'.fonts',Path.home()/'.local'/'share'/'fonts']
    windir=os.environ.get('WINDIR')
    if windir: roots.append(Path(windir)/'Fonts')
    roots.append(Path.home()/'AppData'/'Local'/'Microsoft'/'Windows'/'Fonts')
    out=[]; seen=set()
    for r in roots:
        if str(r) not in seen: seen.add(str(r)); out.append(r)
    return out

def find_font_file(role):
    roots=font_search_roots()
    for filename in FONT_CANDIDATES[role]:
        for root in roots:
            direct=root/filename
            if direct.is_file(): return direct
        for root in roots:
            if not root.exists() or not root.is_dir(): continue
            try:
                for match in root.rglob(filename):
                    if match.is_file(): return match
            except (OSError,PermissionError): continue
    raise RenderError(f"Required Inter font for role '{role}' was not found.")
@lru_cache(None)
def font_path(role): return str(find_font_file(role))
@lru_cache(None)
def get_font(role,size): return ImageFont.truetype(font_path(role),size=size)

def advance(font,text):
    if not text: return 0.0
    return float(font.getlength(text)) if hasattr(font,'getlength') else float(font.getbbox(text)[2]-font.getbbox(text)[0])
def tracked_width(text,font,tracking=0.0): return sum(advance(font,c) for c in text)+tracking*max(0,len(text)-1)
def base_line_height(font,leading=1.15):
    a,d=font.getmetrics(); return int(math.ceil((a+d)*leading))
def draw_tracked_text(draw,x,y,text,font,fill,tracking=0.0):
    cursor=float(x)
    for i,c in enumerate(text):
        draw.text((cursor,y),c,font=font,fill=fill); cursor += advance(font,c)+(tracking if i<len(text)-1 else 0)
    return cursor
def tracked_text_bbox_bottom(draw,x,y,text,font): return float(draw.textbbox((x,y),text,font=font)[3])

def break_long_word(word,font,max_width,tracking):
    chunks=[]; current=''
    for ch in word:
        cand=current+ch
        if current and tracked_width(cand,font,tracking)>max_width: chunks.append(current); current=ch
        else: current=cand
    if current: chunks.append(current)
    if any(tracked_width(c,font,tracking)>max_width for c in chunks): raise RenderError(f"Unable to break token {word!r}")
    return chunks

def wrap_plain(text,font,max_width,tracking=0.0,break_long_words=False):
    text=text.strip()
    if not text: return []
    words=[]
    for word in text.split():
        if tracked_width(word,font,tracking)<=max_width: words.append(word)
        elif break_long_words: words += break_long_word(word,font,max_width,tracking)
        else: raise RenderError(f"Text token is wider than its fixed box and cannot wrap: {word!r}")
    lines=[]; current=''
    for word in words:
        cand=word if not current else current+' '+word
        if tracked_width(cand,font,tracking)<=max_width: current=cand
        else: lines.append(current); current=word
    if current: lines.append(current)
    return lines

def wrapped_height(lines,font,leading=1.15): return len(lines)*base_line_height(font,leading) if lines else 0

def draw_plain_lines(draw,x,y,lines,font,fill,tracking=0.0,leading=1.15):
    if not lines: return y,y
    lh=base_line_height(font,leading); cy=float(y); last=float(y)
    for line in lines:
        draw_tracked_text(draw,x,cy,line,font,fill,tracking); last=tracked_text_bbox_bottom(draw,x,cy,line,font); cy += lh
    return cy,last

def get_accent_span(text,phrase):
    if not phrase: raise RenderError("BRIEF['accent_phrase'] cannot be empty.")
    if text.count(phrase)!=1: raise RenderError('Accent phrase must occur exactly once inside thesis.')
    wc=len(phrase.split())
    if not 3<=wc<=5: raise RenderError('Accent phrase must contain 3 to 5 words.')
    s=text.index(phrase); e=s+len(phrase)
    if s>0 and text[s-1].isalnum(): raise RenderError('Accent phrase begins inside a word.')
    if e<len(text) and text[e].isalnum(): raise RenderError('Accent phrase ends inside a word.')
    return s,e

def wrap_word_spans(text,font,max_width,tracking):
    words=[(m.group(0),m.start(),m.end()) for m in re.finditer(r'\S+',text)]
    space=tracked_width(' ',font,tracking); lines=[]; current=[]; cw=0.0
    for word,s,e in words:
        ww=tracked_width(word,font,tracking)
        if ww>max_width: raise RenderError(f'Thesis word wider than box: {word!r}')
        extra=ww if not current else space+ww
        if current and cw+extra>max_width: lines.append(current); current=[(word,s,e)]; cw=ww
        else: current.append((word,s,e)); cw += extra
    if current: lines.append(current)
    return lines

def draw_accent_paragraph(draw,x,y,text,accent_phrase,font,normal_fill,accent_fill,max_width,tracking,leading):
    a0,a1=get_accent_span(text,accent_phrase); lines=wrap_word_spans(text,font,max_width,tracking); lh=base_line_height(font,leading); cy=float(y); last=float(y); sw=tracked_width(' ',font,tracking)
    for line in lines:
        cx=float(x)
        for i,(word,s,e) in enumerate(line):
            if i: cx += sw
            overlap = max(0, min(e, a1) - max(s, a0))
            fill = accent_fill if overlap > 1 else normal_fill
            draw_tracked_text(draw,cx,cy,word,font,fill,tracking); cx += tracked_width(word,font,tracking)
        last=tracked_text_bbox_bottom(draw,x,cy,' '.join(w for w,_,_ in line),font); cy += lh
    return cy,last

def parse_iso_date(v):
    try: return datetime.strptime(v,'%Y-%m-%d')
    except ValueError as e: raise RenderError(f'Expected YYYY-MM-DD date, got {v!r}') from e
def display_date(v):
    dt=parse_iso_date(v); return f"{dt.day} {dt.strftime('%b %Y').upper()}"
REQUIRED_ITEM_FIELDS={'name','release_date'}
def validate_brief(brief):
    required={'date','layout','slide_count','thesis','accent_phrase','read_through','items','footer_sources'}
    missing=required-set(brief)
    if missing: raise RenderError(f'BRIEF missing keys: {sorted(missing)}')
    parse_iso_date(str(brief['date'])); get_accent_span(str(brief['thesis']),str(brief['accent_phrase']))
    layout=str(brief['layout']).lower(); sc=int(brief['slide_count']); items=brief['items']
    if not isinstance(items,list) or not items: raise RenderError("BRIEF['items'] must contain at least one item.")
    for i,item in enumerate(items,1):
        missing=REQUIRED_ITEM_FIELDS-set(item)
        if missing: raise RenderError(f'Item {i} missing {sorted(missing)}')
        parse_iso_date(str(item['release_date']))
    if layout=='single':
        if sc!=1: raise RenderError('Single layout requires slide_count == 1.')
        if not 1<=len(items)<=3: raise RenderError('Single layout supports 1 to 3 cards.')
    elif layout=='carousel':
        if not 3<=sc<=5: raise RenderError('Carousel slide_count must be 3..5.')
        if sc!=len(items)+2: raise RenderError('Carousel slide_count must equal len(items)+2.')
    else: raise RenderError("layout must be 'single' or 'carousel'")

def load_logo(path):
    if not path.is_file(): raise RenderError(f'Dockfinity logo file does not exist: {path}')
    return Image.open(path).convert('RGBA')
def paste_logo(canvas,logo):
    ratio=LOGO_W/logo.width; h=int(round(logo.height*ratio)); resized=logo.resize((LOGO_W,h),Image.Resampling.LANCZOS)
    if LOGO_Y+h>=EYEBROW_Y-16: raise RenderError('Dockfinity logo is too tall for fixed header geometry.')
    canvas.paste(resized,(LOGO_X,LOGO_Y),resized)
def draw_divider(draw): draw.line([(MARGIN_X,FOOTER_DIVIDER_Y),(WIDTH-MARGIN_X,FOOTER_DIVIDER_Y)],fill=DIVIDER,width=1)

def distribute_column(heights,column_name):
    available=float(AVAILABLE_CONTENT_HEIGHT); content=float(sum(heights)); gaps=len(heights)+1; spacing=(available-content)/gaps
    if spacing<MIN_VERTICAL_SPACING: raise RenderError(f"Column '{column_name}' is overfull.\nAvailable: {available:.1f}px\nContent: {content:.1f}px\nComputed spacing: {spacing:.1f}px\nMinimum permitted: {MIN_VERTICAL_SPACING:.1f}px")
    if spacing>MAX_VERTICAL_SPACING: raise RenderError(f"Column '{column_name}' is underfull.\nAvailable: {available:.1f}px\nContent: {content:.1f}px\nComputed spacing: {spacing:.1f}px\nMaximum permitted: {MAX_VERTICAL_SPACING:.1f}px")
    positions=[]; cursor=CONTENT_TOP+spacing
    for h in heights: positions.append(int(round(cursor))); cursor += h+spacing
    last_bottom=positions[-1]+heights[-1]; gap=FOOTER_DIVIDER_Y-last_bottom
    if abs(gap-spacing)>4: raise RenderError(f"Column '{column_name}' failed vertical-distribution check.")
    return positions,spacing,float(gap)

def item_card_measure(item,width):
    nf=get_font('display_semibold',FONT_SIZE['item_name']); mf=get_font('regular',FONT_SIZE['item_meta']); tw=width-2*ITEM_PAD_X-ITEM_NUMBER_W
    lines=wrap_plain(str(item['name']),nf,tw,tracking=TRACKING['item_name']); meta=(f"{item['version']}  ·  " if item.get('version') else '')+display_date(str(item['release_date']))
    h=ITEM_PAD_Y+wrapped_height(lines,nf,1.08)+ITEM_TEXT_GAP+base_line_height(mf,1.05)+ITEM_PAD_Y
    return int(math.ceil(h)),lines,meta

def render_item_card(draw,x,y,width,index,item,fill=CARD):
    height,lines,meta=item_card_measure(item,width); draw.rounded_rectangle([x,y,x+width,y+height],radius=CARD_RADIUS,fill=fill)
    numf=get_font('semibold',FONT_SIZE['item_number']); nf=get_font('display_semibold',FONT_SIZE['item_name']); mf=get_font('regular',FONT_SIZE['item_meta']); tx=x+ITEM_PAD_X+ITEM_NUMBER_W; cy=y+ITEM_PAD_Y
    draw_tracked_text(draw,x+ITEM_PAD_X,cy+4,f'{index:02d}',numf,ACCENT,0.4); logical,_=draw_plain_lines(draw,tx,cy,lines,nf,TEXT,tracking=TRACKING['item_name'],leading=1.08); my=logical+ITEM_TEXT_GAP
    d=display_date(str(item['release_date']))
    if item.get('version'): ve=draw_tracked_text(draw,tx,my,str(item['version']),mf,ACCENT,0); se=draw_tracked_text(draw,ve,my,'  ·  ',mf,FAINT,0); draw_tracked_text(draw,se,my,d,mf,MUTED,0)
    else: draw_tracked_text(draw,tx,my,d,mf,MUTED,0)
    bottom=float(draw.textbbox((tx,my),meta,font=mf)[3]); return float(y+height)-bottom

def readthrough_measure(text,width):
    bf=get_font('regular',FONT_SIZE['read_through']); lines=wrap_plain(text,bf,width-2*PANEL_PAD_X); lf=get_font('semibold',FONT_SIZE['panel_label'])
    h=PANEL_PAD_Y+base_line_height(lf,1.0)+16+wrapped_height(lines,bf,1.22)+PANEL_PAD_Y
    return int(math.ceil(h)),lines

def render_readthrough_panel(draw,x,y,width,text,fill=PANEL):
    height,lines=readthrough_measure(text,width); draw.rounded_rectangle([x,y,x+width,y+height],radius=PANEL_RADIUS,fill=fill); lf=get_font('semibold',FONT_SIZE['panel_label']); bf=get_font('regular',FONT_SIZE['read_through']); cy=y+PANEL_PAD_Y
    draw_tracked_text(draw,x+PANEL_PAD_X,cy,'READ THROUGH',lf,MUTED,TRACKING['panel_label']); cy += base_line_height(lf,1.0)+16; _,last=draw_plain_lines(draw,x+PANEL_PAD_X,cy,lines,bf,TEXT,leading=1.22)
    return float(y+height)-last

def render_header_base(canvas,draw,logo,brief,carousel_label=None):
    paste_logo(canvas,logo); df=get_font('semibold',FONT_SIZE['date']); dt=display_date(str(brief['date'])); dw=tracked_width(dt,df,TRACKING['date']); draw_tracked_text(draw,DATE_RIGHT-dw,DATE_Y,dt,df,MUTED,TRACKING['date']); ef=get_font('semibold',FONT_SIZE['eyebrow']); draw_tracked_text(draw,EYEBROW_X,EYEBROW_Y,'DOCKFINITY / DISCOVERY',ef,ACCENT,TRACKING['eyebrow'])

def render_single_thesis(draw,brief):
    tf=get_font('display_bold',FONT_SIZE['thesis']); bottom,_=draw_accent_paragraph(draw,x=SINGLE_THESIS_X,y=SINGLE_THESIS_Y,text=str(brief['thesis']),accent_phrase=str(brief['accent_phrase']),font=tf,normal_fill=TEXT,accent_fill=ACCENT,max_width=SINGLE_THESIS_W,tracking=TRACKING['thesis'],leading=1.08)
    if bottom>HEADER_CONTENT_LIMIT: raise RenderError(f'Thesis does not fit above fixed content region.\nThesis bottom: {bottom:.1f}px\nMaximum: {HEADER_CONTENT_LIMIT}px')

def item_footer_metadata(item,index): return ' · '.join([f'{index:02d}']+[str(item[k]) for k in ('licence','platform','repo_url','product_url') if item.get(k)])
def draw_footer_column(draw,x,y,width,label,entries):
    lf=get_font('semibold',FONT_SIZE['footer_label']); bf=get_font('regular',FONT_SIZE['footer']); draw_tracked_text(draw,x,y,label.upper(),lf,MUTED,TRACKING['footer_label']); cy=y+24; lh=base_line_height(bf,1.18); last=float(cy)
    for ei,entry in enumerate(entries):
        lines=wrap_plain(str(entry),bf,width,break_long_words=True)
        for line in lines:
            draw.text((x,cy),line,font=bf,fill=FAINT); last=float(draw.textbbox((x,cy),line,font=bf)[3]); cy+=lh
        if ei<len(entries)-1: cy+=5
    return last

def render_footer(draw,brief,slide_no,slide_count,metadata_entries):
    draw_divider(draw); mb=draw_footer_column(draw,x=FOOTER_META_X,y=FOOTER_TOP,width=FOOTER_META_W,label='Metadata',entries=metadata_entries); sb=draw_footer_column(draw,x=FOOTER_SOURCE_X,y=FOOTER_TOP,width=FOOTER_SOURCE_W,label='Sources',entries=[str(x) for x in brief['footer_sources']]); bottom=max(mb,sb)
    if bottom>FOOTER_TEXT_MAX_Y: raise RenderError(f'Footer content exceeds fixed footer region.\nRendered bottom: {bottom:.1f}px\nMaximum footer text Y: {FOOTER_TEXT_MAX_Y}px')
    pf=get_font('semibold',FONT_SIZE['page']); pt='01 / 01'; pw=advance(pf,pt); draw.text((WIDTH-MARGIN_X-pw,PAGE_NUMBER_Y),pt,font=pf,fill=MUTED); bbox=draw.textbbox((WIDTH-MARGIN_X-pw,PAGE_NUMBER_Y),pt,font=pf)
    if bbox[3]>MAX_RENDER_Y: raise RenderError(f'Page number crosses y={MAX_RENDER_Y}.')

def finalise_slide_metrics(slide_no,clearances,column_metrics):
    tight=min(clearances); print(f'Image {slide_no}: tightest clearance {tight:.1f}px.')
    if tight<MIN_PANEL_CLEARANCE: raise RenderError(f'Image {slide_no} failed clearance requirement.\nTightest clearance: {tight:.1f}px\nRequired minimum: {MIN_PANEL_CLEARANCE:.1f}px')
    for name,spacing,gap in column_metrics:
        print(f'Image {slide_no}, column {name}: spacing {spacing:.1f}px, gap above divider {gap:.1f}px.')
        if abs(spacing-gap)>4: raise RenderError(f'Image {slide_no}, column {name} failed equal-gap test.')
def new_canvas():
    im=Image.new('RGB',(WIDTH,HEIGHT),BG); return im,ImageDraw.Draw(im)
def render_single(brief,logo):
    im,draw=new_canvas(); render_header_base(im,draw,logo,brief); render_single_thesis(draw,brief); items=brief['items']; lhs=[item_card_measure(i,LEFT_W)[0] for i in items]; rh=readthrough_measure(str(brief['read_through']),RIGHT_W)[0]; lp,ls,lg=distribute_column(lhs,'left'); rp,rs,rg=distribute_column([rh],'right'); clear=[]
    for idx,(item,y) in enumerate(zip(items,lp),1): clear.append(render_item_card(draw,x=LEFT_X,y=y,width=LEFT_W,index=idx,item=item))
    clear.append(render_readthrough_panel(draw,x=RIGHT_X,y=rp[0],width=RIGHT_W,text=str(brief['read_through']))); meta=[item_footer_metadata(i,idx) for idx,i in enumerate(items,1)]; render_footer(draw,brief,1,1,meta); finalise_slide_metrics(1,clear,[('left',ls,lg),('right',rs,rg)]); return im
def save_outputs(brief,images,outdir):
    outdir.mkdir(parents=True,exist_ok=True); p=outdir/f"dockfinity-discovery-{brief['date']}.png"; images[0].save(p,format='PNG',optimize=True); return [p]
def main():
    p=argparse.ArgumentParser(); p.add_argument('--logo',required=True,type=Path); p.add_argument('--out-dir',type=Path,default=Path('.')); a=p.parse_args(); validate_brief(BRIEF)
    for role in ('display_bold','display_semibold','regular','semibold'): print(f'Font {role}: {font_path(role)}')
    logo=load_logo(a.logo); images=[render_single(BRIEF,logo)]; paths=save_outputs(BRIEF,images,a.out_dir)
    for path in paths: print(f'Saved: {path.resolve()}')
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except RenderError as exc:
        print(f'\nRENDER ERROR:\n{exc}',file=sys.stderr); raise SystemExit(1)
