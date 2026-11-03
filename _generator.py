#!/usr/bin/env python3
"""Generator stopek mailowych HAIRISHED.

Jeden szablon -> pliki dla kazdej osoby z listy PEOPLE.
Zmiana adresu hostingu = zmiana BASE_URL i ponowne uruchomienie.
"""
import html, json, os, sys

BASE_URL = "https://piolun-00.github.io/hairished-email/"   # <- tu podmieniasz adres hostingu
OUT = sys.argv[1] if len(sys.argv) > 1 else "out"

PEOPLE = [
    {"slug": "helena", "name": "Helena Karaplios", "role": "Founder",
     "phone": "+48 662 060 956", "email": "helena@hairished.com"},
    # {"slug": "stathis", "name": "Stathis Karaplios", "role": "Founder",
    #  "phone": "+48 602 500 401", "email": "stathis@hairished.com"},
]

WEB = "hairished.com"
RED, WHITE = "#830010", "#ffffff"
SERIF = "'DGM Gleff', Georgia, 'Times New Roman', serif"
MONO = "'Ufficio Mono', Menlo, Consolas, 'Courier New', monospace"

DISCLAIMER = (
    "©2026 HAIRISHED®. WSZELKIE PRAWA ZASTRZEŻONE. TREŚĆ TEJ WIADOMOŚCI WRAZ "
    "Z ZAŁĄCZNIKAMI JEST POUFNA I PRZEZNACZONA WYŁĄCZNIE DLA ADRESATA. JEŚLI "
    "WIADOMOŚĆ TRAFIŁA DO CIEBIE PRZEZ POMYŁKĘ, POINFORMUJ NADAWCĘ I USUŃ JĄ "
    "— JEJ KOPIOWANIE, ROZPOWSZECHNIANIE LUB WYKORZYSTYWANIE JEST ZABRONIONE. "
    "ZNAKI TOWAROWE ORAZ ELEMENTY IDENTYFIKACJI WIZUALNEJ HAIRISHED® SĄ "
    "CHRONIONE PRAWEM."
)


def dark_rules(prefix=""):
    """Reguły trybu ciemnego. prefix='' -> produkcja, '.sim-dark ' -> podgląd."""
    p = prefix
    return f"""
{p}.hs-txt, {p}.hs-txt a {{ color:{WHITE} !important; }}
{p}.hs-light {{ display:none !important; }}
{p}.hs-dark {{ display:block !important; max-height:none !important; overflow:visible !important; }}"""


def style_block(base, preview=False):
    fonts = f"""
@media screen {{
  @font-face {{ font-family:'DGM Gleff'; font-weight:400; font-style:normal;
    src:url('{base}fonty/dgm-gleff-regular.woff2') format('woff2'), url('{base}fonty/dgm-gleff-regular.woff') format('woff'); }}
  @font-face {{ font-family:'Ufficio Mono'; font-weight:400; font-style:normal;
    src:url('{base}fonty/ufficio-mono-400.woff2') format('woff2'), url('{base}fonty/ufficio-mono-400.woff') format('woff'); }}
}}"""
    common = """
.hs-txt a { text-decoration:none !important; }
a[x-apple-data-detectors] { color:inherit !important; text-decoration:none !important; }"""
    dark = f"""
@media (prefers-color-scheme: dark) {{{dark_rules()}
}}
[data-ogsc] .hs-txt, [data-ogsc] .hs-txt a {{ color:{WHITE} !important; }}
[data-ogsc] .hs-light {{ display:none !important; }}
[data-ogsc] .hs-dark {{ display:block !important; max-height:none !important; overflow:visible !important; }}"""
    if preview:  # w podglądzie tryb ciemny tylko w prawym panelu, niezależnie od ustawień Maca
        dark = dark_rules(".sim-dark ")
    mso = ("<!--[if mso]><style>.hs-txt{font-family:Georgia,serif !important;}"
           ".hs-mono{font-family:'Courier New',monospace !important;}</style><![endif]-->")
    return f"<style>{fonts}{common}{dark}\n</style>" + ("" if preview else "\n" + mso)


def img_pair(base, name, w, h, alt):
    """Dwa obrazki: jasny widoczny domyślnie, ciemny ukryty (Outlook go nie widzi wcale)."""
    light = (f'<img class="hs-light" src="{base}obrazki/{name}-light.png" width="{w}" height="{h}" '
             f'alt="{alt}" style="display:block;width:{w}px;height:{h}px;border:0;outline:none;">')
    dark = (f'<!--[if !mso]><!--><div class="hs-dark" style="display:none;max-height:0;overflow:hidden;">'
            f'<img src="{base}obrazki/{name}-dark.png" width="{w}" height="{h}" alt="{alt}" '
            f'style="display:block;width:{w}px;height:{h}px;border:0;outline:none;"></div><!--<![endif]-->')
    return light + dark


def signature(p, base):
    e = html.escape
    txt = f"font-family:{SERIF};font-size:12px;line-height:14px;color:{RED};mso-line-height-rule:exactly;"
    a = f"color:{RED};text-decoration:none;"
    tel = "tel:" + p["phone"].replace(" ", "")
    return f"""<!--[if mso]><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<table role="presentation" class="hs-sig" cellpadding="0" cellspacing="0" border="0" width="100%" style="width:100%;max-width:600px;border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">
  <tr><td class="hs-txt" style="{txt}padding:0 0 27px 0;">{e(p['name'])}<br>{e(p['role'])}</td></tr>
  <tr><td style="padding:0 0 27px 0;"><a href="https://{WEB}" style="{a}">{img_pair(base, 'logo', 207, 15, 'HAIRISHED')}</a></td></tr>
  <tr><td class="hs-txt" style="{txt}padding:0 0 15px 0;"><a href="{tel}" style="{a}">{e(p['phone'])}</a><br><a href="mailto:{p['email']}" style="{a}">{e(p['email'])}</a><br><a href="https://{WEB}" style="{a}">{WEB}</a></td></tr>
  <tr><td style="padding:0 0 15px 0;">{img_pair(base, 'sygnet', 40, 30, 'HAIRISHED – sygnet')}</td></tr>
  <tr><td class="hs-txt hs-mono" style="font-family:{MONO};font-size:7px;line-height:10px;color:{RED};mso-line-height-rule:exactly;-webkit-text-size-adjust:none;text-size-adjust:none;">{e(DISCLAIMER)}</td></tr>
</table>
<!--[if mso]></td></tr></table><![endif]-->"""


def production(p):
    """Plik do instalacji: Apple Mail, Thunderbird, Outlook (.htm)."""
    return f"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark">
<title>Stopka – {html.escape(p['name'])}</title>
{style_block(BASE_URL)}
</head><body style="margin:0;padding:0;">
{signature(p, BASE_URL)}
</body></html>
"""


def preview(p):
    """Podgląd lokalny (obrazki z dysku) + przycisk kopiowania wersji produkcyjnej."""
    local = signature(p, "")
    prod = signature(p, BASE_URL)
    return f"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Podgląd stopki – {html.escape(p['name'])}</title>
{style_block("", preview=True)}
<style>
  body {{ margin:0; font:14px/1.5 -apple-system,BlinkMacSystemFont,'Helvetica Neue',sans-serif; background:#ececec; color:#222; }}
  header {{ padding:24px 32px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
  header h1 {{ font-size:16px; font-weight:600; margin:0 16px 0 0; }}
  button {{ font:inherit; padding:8px 14px; border-radius:6px; border:1px solid #bbb; background:#fff; cursor:pointer; }}
  button.primary {{ background:#830010; color:#fff; border-color:#830010; }}
  #msg {{ color:#2a7a2a; }}
  .panes {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(680px,1fr)); gap:24px; padding:0 32px 32px; }}
  .pane {{ border-radius:12px; padding:40px; }}
  .pane .label {{ font-size:12px; text-transform:uppercase; letter-spacing:.06em; opacity:.55; margin-bottom:28px; }}
  .pane .mail {{ margin-bottom:28px; font:14px/1.5 -apple-system,sans-serif; }}
  .light {{ background:#fff; color:#222; }}
  .sim-dark {{ background:#1e1e1e; color:#eee; }}
  .sim-dark.graphite {{ background:#383838; }}
  #clip {{ position:fixed; left:-9999px; top:0; background:#fff; }}
</style></head>
<body>
<header>
  <h1>{html.escape(p['name'])} — stopka HAIRISHED</h1>
  <button class="primary" onclick="copySig()">Kopiuj stopkę (do Gmaila / Outlooka)</button>
  <button onclick="document.querySelectorAll('.sim-dark').forEach(e=>e.classList.toggle('graphite'))">Tło trybu ciemnego: czarne / grafit</button>
  <span id="msg"></span>
</header>
<div class="panes">
  <div class="pane light"><div class="label">Tryb jasny</div><div class="mail">Dzień dobry,<br>przesyłam materiały w załączniku.<br><br>Pozdrawiam</div>{local}</div>
  <div class="pane sim-dark"><div class="label">Tryb ciemny (symulacja)</div><div class="mail">Dzień dobry,<br>przesyłam materiały w załączniku.<br><br>Pozdrawiam</div>{local}</div>
</div>
<div id="clip" contenteditable="true">{prod}</div>
<script>
function copySig(){{
  const el=document.getElementById('clip'), r=document.createRange(), s=getSelection();
  r.selectNodeContents(el); s.removeAllRanges(); s.addRange(r);
  let ok=false; try{{ ok=document.execCommand('copy'); }}catch(e){{}}
  s.removeAllRanges();
  document.getElementById('msg').textContent = ok
    ? 'Skopiowano. Wklej w ustawieniach podpisu (Cmd+V).'
    : 'Nie udało się — zaznacz stopkę ręcznie i skopiuj.';
}}
</script>
</body></html>
"""


def apple_mail(p):
    """Treść do wklejenia w plik .mailsignature (Apple Mail) – style + stopka, bez <html>/<head>."""
    return style_block(BASE_URL) + "\n" + signature(p, BASE_URL) + "\n"


os.makedirs(OUT, exist_ok=True)
for p in PEOPLE:
    with open(os.path.join(OUT, f"stopka-{p['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(production(p))
    with open(os.path.join(OUT, f"podglad-{p['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(preview(p))
    with open(os.path.join(OUT, f"apple-mail-{p['slug']}.txt"), "w", encoding="utf-8") as f:
        f.write(apple_mail(p))
    print(p["slug"], "dlugosc HTML do Gmaila:", len(signature(p, BASE_URL)), "znakow (limit 10000)")
print("ok:", [p["slug"] for p in PEOPLE], "->", OUT)
