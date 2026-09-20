METAL DOCK — DAILY STAINLESS RAW-MATERIAL BRIEF
THE SPECIFICATION

This file is the whole specification. The scheduled task holds nothing but a
pointer to it, and fetches it at the start of every run.

It lives here rather than in the task prompt for two reasons. A scheduled run
does not reliably reopen the conversation the task was written in, so a
specification that lives in that conversation is not there when the run needs
it - on 17 September 2026 a run stopped for exactly that reason. And every
amendment used to be pasted on top of the last one, so the prompt accumulated
three filing instructions and two copies of the same four corrections. A file
can be edited in place.

Nothing renders here. The slides are drawn by GitHub Actions from the JSON in
section 7, after the brief is filed. This task produces text and JSON.

--------------------------------------------------------------------------

0. RUN ISOLATION, AND THE ONE EXCEPTION
--------------------------------------------------------------------------

Every scheduled run is absolutely isolated. Use only data researched in that
run. Never carry forward a figure, an item, a phrase or a claim from an earlier
run. Never reuse an earlier run's headline.

The single exception is a same-day repair. If the owner asks you to correct
something in a brief you already produced today, that is a repair, not a new
run: keep that run's figures, sources and dates exactly as they are and change
only what was asked for. Do not re-research. Run isolation applies between
scheduled runs, not between a run and its own repair.

Web search is required for this task and is always permitted - this rule does
not restrict it. Nor does it restrict the Gmail and GitHub connectors named in
section 9, which are how the brief is filed. What it restricts is everything
else: do not call, open or request permission for any other connector. No
Drive, no Figma, no design tools, no image generation - this task draws
nothing. An approval prompt pauses a scheduled run and the day is lost.
If you find yourself about to trigger one, stop and produce the output with what
you have.

Put the written brief in the message body as plain readable text. Do not hide
any part of it behind a collapsed "worked for N minutes" block, a file or a
canvas. The whole brief must be visible without clicking anything.

Show only the final output. If you produced something and then rejected it - a
discarded paragraph, a figure that would not reconcile - do not display it. Say
in one line that it was rejected and why, and show only what is actually part
of the brief. A rejected draft sitting in the reply can be mistaken for the
deliverable and posted.

--------------------------------------------------------------------------
1. SOURCES
--------------------------------------------------------------------------

Trusted sources, by name:
  SMM (metal.com) - China stainless, nickel, NPI, Indonesian HMA, LME nickel
  SHFE (shfe.com.cn) - stainless futures and inventory
  LME (lme.com) - nickel price and stocks
  BigMint (bigmint.co) - Indian stainless benchmarks and scrap
  DGTR - trade remedies
  BIS and Ministry of Steel - standards, QCO
  Jindal Stainless and JSW investor pages - company news
  EEPC India and Ministry of Commerce - utensils and cookware trade data

Page patterns that are known to work:
  SMM articles:  https://news.metal.com/newscontent/{numeric-id}-{slug}
  SMM LME page:  https://www-old.metal.com/nickel/LME_NI_3M
  LME nickel history, dated and public:
                 https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Ni_cash
  DGTR:          the individual case page, never dgtr.gov.in
Do not treat www-old.metal.com/Nickel/ as evidence. It is a category board, not
a page carrying a specific fact.

Known source behaviour, so you do not waste the run rediscovering it:
  SMM articles reliably carry the numbers. In practice the SHFE stainless figure
  and the LME nickel figure both arrive through SMM rather than through the SHFE
  or LME sites directly. Still check the primary sites; if they do not yield a
  dated exact figure, use SMM and attribute it to SMM, not to SHFE or LME.
  BigMint's public pages show categories, series names and row dates, but the
  grade-level numeric matrix is usually gated. That is a genuine specialist
  paywall and may be declared publicly.

  THE NICKEL FIGURE COMES FROM WESTMETALL, NOT FROM SMM. This is the one place
  the specification overrides "use SMM", and it is worth reading twice, because
  getting it wrong has now cost four consecutive briefs.

  The SMM LME_NI_3M page shows exactly two numbers: the live quote and the
  previous close. Its dated history table is behind a login and every row reads
  "login to view". So the page can tell you today's number and yesterday's, and
  nothing before that - which is precisely what a change figure needs. Between
  15 and 18 September 2026 the nickel line was wrong every single day: once from
  a news article that mentioned nickel in passing, and three times from a prior
  close that could not actually be read anywhere.

  Westmetall publishes the LME official cash settlement and the official
  3-month closing price for every trading day, dated, free, in a plain table:

    https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Ni_cash

  Read the column headed "LME Nickel 3-month". Take the row for the session the
  brief is reporting - the brief dated D reports the last completed session
  before D - and compute the change against the row immediately below it, which
  is the previous trading day. Both numbers come off the same table, so the
  change is arithmetic, not a second lookup.

  Attribute it to Westmetall, citing that URL, and say it is the LME official
  3-month closing price. Do not attribute it to SMM and do not quote SMM's
  figure for it: SMM's quote is an intraday LMEselect snapshot taken in Asian
  hours and runs some tens of dollars away from the official close. They are two
  different series and mixing them across days produces a change that is real in
  neither.

  SMM remains the source for everything else on the nickel side - NPI, ore,
  Indonesian HMA, Chinese stainless - and for the commentary. It is only the
  NI-3M benchmark figure that moves to Westmetall.

Do not mark anything unverified without actually trying the trusted sources
first. "Not found" is a conclusion you reach after looking, never a default.

Do not search USD/INR or CNY/INR. The reason, so you do not try to be helpful:
RBI stopped publishing reference rates in 2018, FBIL's public table lags and
carries no CNY/INR pair, and NSE's page is not reliably retrievable. There is no
public source worth the run. FX is not a gap to announce; it is a deliberate
omission. Never mention it in the post or the JSON.

Do not search public patta or secondary-market levels for Jodhpur, Mumbai,
Delhi or Ahmedabad. The reason: it is a relationship market with no public
tape. No public number for it is trustworthy.

If the owner has pasted FX or patta figures into the conversation, you may use
them, attributed as "operator input, [date]".

--------------------------------------------------------------------------
2. FRESHNESS AND SETTLED SCOPE
--------------------------------------------------------------------------

Prices and inventory: within the last 2 trading sessions.
News and announcements: within the last 7 days.
Policy and case status: current as of the run date.

DGTR case 06/28/2025-DGTR. The product scope is settled - do not re-derive it,
and do not spend the run re-reading it. Report only changes in status, new
filings, hearings, preliminary findings or final determination.
Settled scope: CR stainless 300 and 400 series from China, Indonesia and
Vietnam; austenitic CR with minimum 6% Ni plus all ferritic and martensitic
grades; coils, sheets, strips, punched coil and circles are covered; HR is
excluded; 201 is excluded; 202 depends on its actual chemistry meeting the 6% Ni
threshold - never classify 202 categorically without chemistry.

--------------------------------------------------------------------------

3. THE INTERNAL BRIEF
--------------------------------------------------------------------------

Output exactly one set of results. Skip a section that has no genuinely new
information. Never pad. Maximum 3 points per section, maximum 70 words per
point.

§1 IMPORT & GLOBAL
SHFE stainless futures price with 1-day and 1-week change, plus inventory
direction; LME nickel price, change and stock direction; public Chinese mill FOB
offers where actual values exist; Indonesian nickel and NPI policy, ore and
smelter disruptions.

Also carry global DEMAND signals, not only price and supply: import and export
volumes, trade-body or Eurostat figures, and producer guidance from the large
mills such as Outokumpu, Acerinox or Aperam. A demand print released today is
fresher than a price from Friday's session and often explains it. On 7 September
this section missed EU H1 stainless imports falling 21% year-on-year with flat
products down 35%, and Outokumpu guiding Q3 volumes down up to 10% - a genuinely
new signal published that morning.

Carry ferrochrome and chrome ore as well, for the 400-series grades: the SMM
high-carbon ferrochrome assessment and, where available, South African chrome
ore or the Chinese ferrochrome tender price, each with its change and its own
date. South Africa and Kazakhstan are the supply side to watch; power costs and
export policy there move this chain the way Indonesian ore moves nickel.

When ferrochrome and nickel move in opposite directions, say so. It means
400-series and 300-series landed costs are diverging, which is directly
actionable for a buyer choosing between 430 and 304 for the same part.

Carry ocean freight on the China-India and Indonesia-India lanes, and any
disruption affecting them - Red Sea routing, congestion, a container rate move
large enough to matter against material cost. Only when it moved; a stable
freight market is not news. Source it from a named index, a carrier or a
trade body, never from an estimate.

If you deliberately omitted commonly available data, say so here and only here -
never in the post or the JSON.

§2 INDIA DOMESTIC
Jindal Stainless and JSW price, capacity, production; SS scrap prices and
availability; grade-specific movement across 201/202/304/316/410/430 in HR and
CR; operator input if supplied.

This section must not come back empty simply because BigMint's price table is
gated. The gate is on the numbers, not on the direction. BigMint's own articles
at bigmint.co/insights/detail/ and bigmint.co/intel/detail/ are free and state
the direction in words - for example that Indian stainless scrap moved up
week-on-week on a supply shortage, or that finished-product prices rose on tight
raw material. Search those article paths every run, and report the direction with
its source and date, stating plainly that the numeric values are subscriber-
gated. A sourced direction is publishable; an invented number is not.

India is the section this brief exists for. A brief that reports only China,
Indonesia and the LME tells an Indian buyer what is happening somewhere else.
When the Indian direction diverges from the global one - global inputs easing
while Indian scrap firms - that divergence is the most valuable thing in the run
and belongs on a slide, not only in the internal brief.

§3 POLICY
DGTR case status per the settled note above; other anti-dumping or safeguard
actions; import duty, BIS, QCO, import licensing; export policy in supplying
countries.

Report any scheduled event inside the next 30 days even when the status is
unchanged: hearings, determination deadlines, duty expiries, comment-period
closes. A date that has not moved is still a date a buyer is planning around.


§4 UTENSILS DEMAND
Cookware and utensil capacity, new plants, launches, export data, demand
signals. This section is often empty. Skip it silently when it is - do not
invent an item to fill it, and do not apologise for it in the post.

§5 MY READ
Maximum 120 words, written as prose, not as bullet points. State the 2-4 week
landed-cost direction and the pace. Then, separately and explicitly, state any
STEP-CHANGE RISK from a duty, policy or supply shock, as distinct from gradual
drift. These two are different forces and must not be blended.

State the 2-4 week direction for the 300-series and the 400-series separately
whenever their input chains diverge. A single landed-cost view across all six
grades hides the divergence that matters most.

--------------------------------------------------------------------------

4. EVIDENCE
--------------------------------------------------------------------------

Every fact entering the post or the JSON carries a named source and a
publication date printed beside it. Every source resolves to the specific page
carrying that fact. A homepage is not a source. For DGTR, link the individual
case page.

An access date is not a publication date. If a source was checked but yielded no
figure - gated, unavailable, nothing new - do not list it as a source at all.

Where a policy item has several relevant dates, keep all of them rather than
inventing a single publication date. For example: notice dated 31 Jul 2026, case
page updated 2 Sep 2026.

Numbers come only from the trusted list. Anything not sourceable that way may
appear only in internal sections tagged [UNVERIFIED] and must never reach the
post or the JSON.

Never write an article number, section number, notification number, regulation
number, case stage or determination that you did not read verbatim on the source
page. Describe the measure in plain words instead. Attributing a specific legal
provision to a government body without having read it is the single most
damaging error this task can make.

Recompute every percentage from the two numbers printed beside it before it
enters the brief, a slide or the JSON. Divide the change by the starting value
and confirm it matches to one decimal place. If it does not match, the figure is
wrong - find the correct starting value, or print the absolute change alone and
drop the percentage.

State in one line at the end of §1 which trading session your figures come from,
so that a mismatch against a previous run is visible.

If you find a credible source that is not on the trusted list, name it at the
end and ask whether to trust it going forward. Do not adopt it silently.

Never publish the owner's buying position, stock levels, margins, target
companies, tenders, plans, what is being built, or any system weakness.

Data gaps: declare a gap publicly only when it is a genuine specialist or
paywalled gap, such as the gated BigMint grade benchmarks. Never publicly
announce an inability to source commonly available data - it reads as
incompetence rather than rigour. Omit those silently.

--------------------------------------------------------------------------
5. THE PUBLIC POST
--------------------------------------------------------------------------

Produce a post only if there is genuinely something worth posting. Otherwise
write 'NO POST TODAY' and go straight to §7.

The post is neutral market analysis, not sales copy. Every item explains what
happened and what it means or who it affects. No buy, sell, hold or price
recommendation of any kind, ever, in any form.

  1. LONG CAPTION for LinkedIn - 120 to 180 words, plain and confident, no
     emojis, opening with the insight rather than a greeting.
  2. SHORT CAPTION for Instagram and WhatsApp Status - 3 to 4 lines, same
     substance, tighter.
  3. X CAPTION - under 280 characters including the source attribution. This is
     a hard limit, not a target. Count the characters and print the count. If it
     does not fit, cut the least important fact, never the source.
     Attribute in the caption as 'Source: SMM, 4 Sep 2026'. Do not paste a raw
     URL into the caption - a long link spends half the budget and leaves room
     for only one fact. The URL requirement applies to the JSON, not to the
     captions.
  4. FACEBOOK CAPTION - the page audience is the trade, so this reads like the
     LinkedIn one rather than the Instagram one, but shorter: 80 to 120 words.
     At most 2200 characters.
  5. THREADS CAPTION - at most 500 characters. This is the platform's own hard
     cap, not a house style: over it the post does not send at all. Count the
     characters and print the count. The X caption usually works here with a
     little more room, but write it as its own line of thought rather than
     pasting the X one and hoping.
  6. 8 hashtags.

Captions carry facts, not the machinery behind them. Never write that a figure
was reconstructed, derived, approximate, or that a comparison base was
recalculated. That belongs in the internal brief. If a figure is too uncertain
to state plainly in public, leave it out of the post.

6. STANDING RULES
--------------------------------------------------------------------------

These were added one at a time after things went wrong. They were held in two
overlapping lists in the task prompt; this is the single copy.

6.1 THE SECTION ROW LISTS ONLY WHAT CARRIED CONTENT
A section that has no item today does not appear in the cover's section row.
On 9 September UTENSILS DEMAND appeared while the closing summary said §4 had
nothing.

6.2 NO METHOD LANGUAGE IN PUBLIC, INCLUDING SINGLE WORDS
Never write recomputed, carried, verified, not publicly verified, searched or
fallback - or any similar word about how the work was done - in a caption or
anywhere in the JSON. Write the market fact instead: '+59.7% from 22.1 kt Ni on
13 Aug', not 'recomputed increase is +59.7%'. The internal brief keeps whatever
process detail it needs; nothing else does.

6.3 THE JSON IS PUBLIC OUTPUT
It publishes to the website, so 6.2 applies to it in full. A change field
carries the change and nothing else. Never record there that a figure could not
be verified, or which searches were run.

6.4 INVENTORY ROWS ARE ALWAYS NEUTRAL
Any benchmark with metricType 'inventory' carries direction 'neutral', without
exception. A falling stock level is not a falling price - the 300-series draw
that came from warrant outflow rather than consumption is exactly why. On
9 September CN-300-SOCIAL-STOCK was 'down' and CN-NPI-PORT-STOCK was 'up'; both
should have been neutral.

6.5 THE DISCLAIMER IS FIXED WORDING
Reproduced character for character:
"Indicative trade intelligence for industrial planning. Every figure carries
its actual verified source and date. For firm contract pricing on specific
coils, circles, or sheets, contact our desk."
It was once changed to 'stated' in place of 'actual verified'. Never reword it.

6.6 THE COVER HEADLINE IS SENTENCE CASE
Like 'Nickel bounces, but NPI buying stays cautious'. Never all capitals. It is
one headline for both the page and the slide cover - there is not a separate
one for each.

6.7 SLIDE COPY RULES THE RENDERER DOES NOT ENFORCE
EVERY entry in the "slides" array carries exactly one "accent", three to five
words, and the website rejects a slide without one. There is no exception for
the first entry.

The cover is not in that array. It is built from "title" and "coverThesis" and
has no accent of its own, which is why older wording said "slide 1 has none" -
that meant the cover, counted as page 1 by the renderer, not slides[0]. On
17 September 2026 that sentence was read the other way and the brief was
rejected for a missing slides[0].accent.

An accent sits on its own line and never breaks a sentence. Nothing decorative
is added to fill space. The tagline is exactly STAINLESS STEEL SUPPLY and the
three rejected taglines never appear.

6.8 SOMETHING MISSED IS CARRIED, ONCE
If something significant from the last 7 days was not carried in an earlier run
- because it fell outside the scope as written, because a source did not load,
or because the run simply missed it - carry it in the next run.

This is not a run-isolation exception and needs none. Run isolation forbids
reusing an earlier run's figures, phrasing or output. Reporting an event that
happened three days ago, researched fresh today from its primary source, is
ordinary research. The date on the item is the event's own date, not today's.

  - Report it with its own date, exactly as on the day it happened.
  - Say in one clause that it is being carried now, in the internal brief only.
    Never on a slide and never in a caption; a reader does not need to know the
    brief was late, and it is method language.
  - It counts against the item cap like any other item.
  - Rank it on what it means today, not on the fact that it was missed. A
    week-old move that changed nothing does not displace something current.
  - An item is only late once. If it was carried in an earlier run, it is done.

--------------------------------------------------------------------------

7. WEBSITE JSON
--------------------------------------------------------------------------

Always produce one fenced JSON block, valid for
content/market-brief/YYYY-MM-DD.json.

Required: date, title, summary, benchmarks, sources.
Optional: briefDate, sessionDate, marketReadStructured, policyWatch,
utensilsImpact.
Never output: marketRead, regulatoryNote, tradingDay, fxNote.

date and briefDate are the run date. sessionDate is the last completed trading
session and is never a weekend or a holiday.

NON-TRADING-DAY RULE. This rule is deterministic, not an editorial choice:

  - On Saturday, Sunday, an exchange holiday, or before a new close exists,
    sessionDate remains the latest completed session shown by the dated source.
  - Never label the publication date as a trading session merely because the
    automation runs that day.
  - If two consecutive publications share sessionDate, the same closing
    benchmark must keep the same value. A changed close requires a new session;
    a correction requires correcting the earlier publication explicitly.
  - A weekend or holiday caption says the actual session date, "Friday close",
    or "latest completed session". It must not say or imply that the closed
    market traded "today".
  - Fresh weekend news, policy, inventory commentary or demand evidence may be
    added only with its own actual source date. It does not turn into a new
    exchange close.

Benchmark fields: name, symbol, value, optional unit, change, direction,
metricType, note, isKeySignal, section, source.
  value carries the complete formatted figure including its unit. For a
  non-numeric direction-only item, value states the actual direction, for
  example 'Up week-on-week'. Never 'N/A', 'Not available', 'Direction only' or
  any other placeholder.
  Omit unit entirely when there is none. Never send an empty string.
  direction uses the weekly trend wherever both daily and weekly exist.
  An inventory row uses metricType 'inventory' and direction 'neutral' - a
  falling inventory is not a falling price.
  isKeySignal is true on exactly one benchmark, false on all the others.
  note is reader-facing content only. It must never contain rendering or
  instruction language.

Only verified items enter the JSON. Every benchmark and policy item carries its
source and date. sources.attribution lists every source used, with dates.
surveyDate is the run date. The disclaimer is exactly:
'Indicative trade intelligence for industrial planning. Every figure carries its
actual verified source and date. For firm contract pricing on specific coils,
circles, or sheets, contact our desk.'

Structure:
{
  "date": "YYYY-MM-DD",
  "briefDate": "Weekday, D Month YYYY",
  "sessionDate": "Weekday, D Month YYYY",
  "title": "short headline thesis",
  "summary": "one or two sentences, used for meta tags and RSS",
  "benchmarks": [{"name":"display name","symbol":"short code","value":"complete formatted figure including its unit","change":"change string","direction":"up | down | neutral","metricType":"price | inventory | spread | other","note":"context only","isKeySignal":false,"section":"China & Global Inputs | India Domestic","source":"Source: NAME, D Mon YYYY - URL of the specific page"}],
  "marketReadStructured": {"bias":"","horizon":"","pace":"","reasoning":"","watch":["",""],"stepChangeRisk":""},
  "policyWatch": [{"id":"","title":"","status":"","detail":"","source":""}],
  "utensilsImpact":"",
  "sources":{"attribution":"every source used, with dates and page URLs","surveyDate":"YYYY-MM-DD","disclaimer":"Indicative trade intelligence for industrial planning. Every figure carries its actual verified source and date. For firm contract pricing on specific coils, circles, or sheets, contact our desk."}
}

The source string carries the specific page URL after the name and date, so that
the JSON itself satisfies the evidence rule rather than relying on links placed
outside the block. Omit optional fields when unavailable rather than sending
empty placeholders.

--------------------------------------------------------------------------


7.1 THE SLIDES
--------------------------------------------------------------------------

The slides are built from this JSON by the website. Add these three fields.

WHY, because this is not housekeeping. On 9 September the page headline read
'Nickel bounces while NPI and India stay cautious' and the slide headline read
'Nickel bounces, but NPI buying stays cautious'. Same brief, same day, two
different headlines. Nothing compared them, so nothing caught it.

  "coverThesis": "<one short sentence under the cover headline>",

  "coverSources": ["<first cover source line>", "<second, optional>"],

  "slides": [
    {
      "eyebrow": "<exactly one of: GLOBAL MARKETS | INDIA DOMESTIC |
                   POLICY UPDATES | UTENSILS DEMAND | MARKET OUTLOOK>",
      "accent": "<three to five words>",
      "headline": "<the slide's headline>",
      "readLabel": "<label on the dark panel, e.g. INPUT READ>",
      "readThrough": "<one or two sentences>",
      "cards": [
        {
          "benchmark": "<symbol of the benchmark this card shows>",
          "label": "<short uppercase label>",
          "value": "<the figure as it should read on the slide>",
          "body": "<one or two sentences of context>"
        }
      ],
      "sources": ["<first source line>", "<second, optional>"]
    }
  ]

RULES THE WEBSITE ENFORCES. A brief that breaks any of these does not publish,
and the reason is written back on the issue.

  a. Two or three cards per slide. One or two source lines per slide. At most
     two cover source lines. Consolidate related material instead of creating
     a one-card slide: the fixed renderer rejects sparse slides as underfilled.

  b. A card that shows a figure MUST carry "benchmark" with the symbol of a
     benchmark in this same brief, and that benchmark's value MUST appear
     inside the card's "value".

       benchmark NI-3M has value  "USD 16,755/mt"
       the card may read          "8 Sep: USD 16,755/mt"     correct
       the card may not read      "8 Sep: USD 16,750/mt"     rejected

     This is the point of the whole change: a slide cannot show a number this
     brief does not publish.

  c. A card that is NOT a figure - a hearing date, a case status, a two-week
     read - carries no "benchmark" key at all. Do not invent a symbol for it.

  d. "eyebrow" must be one of the five names above, spelled exactly. These are
     the slide's own section names, NOT a benchmark's "section" field.

  e. "title" is the headline for both the page and the slide cover. If the
     build reports it is too deep for the cover, shorten "title" - and the page
     gets the shorter headline too. That is correct: they are one headline.
     Keep title at 48 characters or fewer and coverThesis at 105 characters or
     fewer; these are the longest proven published bounds for the fixed cover.

7.2 THE CAPTIONS
--------------------------------------------------------------------------

The captions written in section 5 also travel in the JSON, so that the words
and the figures come from one source and reach the posting queue together.

  "social": {
    "linkedin":  "<the LinkedIn caption from section 5>",
    "instagram": "<the Instagram / WhatsApp caption from section 5>",
    "x":         "<the X caption from section 5, WITHOUT the hashtags>",
    "facebook":  "<the Facebook caption from section 5>",
    "threads":   "<the Threads caption from section 5>",
    "hashtags":  ["#Example", "#AnotherOne"]
  }

  a. All six keys required, none empty. Facebook and Threads became required
     on 20 September 2026; briefs dated before that carry only the first three
     and remain valid.
  b. Lengths, measured on the caption alone: x at most 280, threads at most
     500, instagram at most 2200, facebook at most 2200, linkedin at most
     3000.
  c. THE X CAPTION CARRIES NO URL AND NO BARE DOMAIN. Not 'https://...', not
     'www.metaldock.co.in', not 'metaldock.co.in' on its own. This is a bill,
     not a style rule: a post carrying a link is charged at $0.20 against
     $0.015 without one. Name the source ('Source: SMM') and leave the address
     out. The rule is only on "x".
  d. Hashtags are a non-empty array, each starting with '#' and then only
     letters, digits or underscores. '#StainlessSteel', never '#Stainless
     Steel'. Keep them OUT of the caption strings - they are appended per
     platform, as many as fit.

WRITING THE JSON: it must parse. Keep every string on one line in the source; a
real line break inside a string is the failure that has actually happened. Use
straight quotes. No trailing commas. No comments.

--------------------------------------------------------------------------

8. SELF-CHECK
--------------------------------------------------------------------------

Carry these out literally and report them honestly. A check you did not
actually perform is reported as not performed, never as a pass. Reporting a
pass on a check you did not run is worse than reporting a failure.

Nothing here concerns a rendered image. The slides are drawn by GitHub Actions
after filing, and it runs its own clearance and spacing checks; on 16 September
a run of this task lost a complete and correct brief because an image check had
been allowed to block the filing.

   1. Every figure in the JSON matches the internal brief digit for digit.
   2. Every percentage divides correctly from the two numbers beside it.
   3. Every figure carries a source and a publication date. No access dates.
      No source listed that yielded nothing.
   4. No legal article, section, notification or case-stage number appears that
      was not read verbatim on the source page.
   5. Nothing in this brief came from an earlier run.
   6. No value contains a placeholder; no note contains instruction language.
   7. No fact, URL, source or date is duplicated inside the same slide object,
      other than the brief date and the session date, which are two different
      dates.
   8. No back-calculated comparison base is printed, and nothing mentions
      reconstruction, derivation or approximation.
   9. Nothing that was generated and then rejected appears in the reply.
  10. No buy, sell or hold language appears anywhere.
  11. Exactly one benchmark carries isKeySignal true.
  12. Every benchmark with metricType 'inventory' carries direction 'neutral'.
      Print that confirmation as part of the schema-enum line.
  13. Every entry in "slides" carries exactly one "accent" of three to five
      words that does not break a sentence. Count them against the number of
      slides and print both: 'accents: N of N slides'. The cover is not in the
      array and is not counted.
  14. The X caption is under 280 characters WITH its hashtags counted, and
      carries no URL and no bare domain. Print the count.
  15. The disclaimer is character for character the wording in 6.5.
  16. The JSON parses.

Print 'Checks: PASS' on one line only if every check either passed or is N/A.
Otherwise state which failed and what was corrected.

Finally, tell the owner which sections had no reliable source that day.

--------------------------------------------------------------------------

9. FILING
--------------------------------------------------------------------------

The production route begins when the clock opens a GitHub issue titled
"research: YYYY-MM-DD". The repository workflow owns the complete run:

  1. The repository fetches the trusted source pages in section 1 directly,
     without a paid search service.
  2. Gemini API 3.5 Flash-Lite analyses the freshly fetched evidence.
  3. A separate Gemini 3.5 Flash-Lite pass writes only the section 7 JSON under
     a response schema. It does not file mail, render, commit or publish.
  4. The repository runs its existing schema validator, previous-brief figure
     reconciliation, independent LME nickel check and cited-URL check.
  5. The deterministic renderer creates the cover and data slides from the
     validated JSON.
  6. Only after every check passes are the JSON and slides committed together.

The previous published brief is comparison context only. It may establish the
earlier value for a stated change, but none of its numbers becomes today's
value without fresh evidence from a trusted source in the current run.

The model's output is data for the validators, not instructions to another
service. Return exactly one JSON object and no route report, code fence,
commentary or self-check transcript.

If a current figure cannot be evidenced, Gemini free quota is exhausted, or
any validator, figure, nickel, URL or render check fails, publish nothing. The
dated issue remains open with the exact failure. Never weaken a check or invent
a number to make a run pass.

MANUAL RECOVERY. A human may still open "brief: YYYY-MM-DD" with the complete
section 7 JSON in its body. That skips Gemini but enters the same validation,
figure, render and publication path. It is recovery, not the scheduled route.

FILING A DATE THAT IS ALREADY PUBLISHED

  The website will not quietly replace a brief that is already on the site.
  If you file a date that exists and your document differs from what is live,
  it is refused unless the issue carries a line beginning "CORRECTION:",
  outside the JSON fence, saying what is being corrected and why.

  This is manual recovery only. A normal `research:` issue never replaces a
  published day. On 19 September 2026 a second valid run silently replaced a
  nine-benchmark brief with a four-benchmark one; the correction guard exists
  so that cannot happen again.
