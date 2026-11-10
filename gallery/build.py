"""Builds the guest gallery from guests.json into public/. Vercel runs it on every push.

Each guest gets /g/<slug>/ behind their own password (see middleware.js). The front page never lists guests.
usage: python3 build.py
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
T = {
    "en": {"enter": "Enter", "password": "Password", "wrong": "That password didn't work. Try again.",
           "download": "Download full quality", "copy": "Copy caption", "copied": "Copied",
           "private": "This is a private page for our guests.", "transcript": "Transcript",
           "kinds": {"episode": "Episode", "spicy": "Spicy cut", "social": "Social clip", "team": "Team social clip",
                     "linkedin": "LinkedIn", "story": "Story"}},
    "es": {"enter": "Entrar", "password": "Contraseña", "wrong": "Esa contraseña no funcionó. Inténtalo de nuevo.",
           "download": "Descargar en calidad completa", "copy": "Copiar texto", "copied": "Copiado",
           "private": "Esta es una página privada para nuestros invitados.", "transcript": "Transcripción",
           "kinds": {"episode": "Episodio", "spicy": "Versión picante", "social": "Clip", "team": "Clip de equipo",
                     "linkedin": "LinkedIn", "story": "Story"}},
}
VERTICAL = {"social", "team", "story"}
e = html.escape


def head(title: str, lang: str) -> str:
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">'
            f'<title>{e(title)}</title><link rel="stylesheet" href="/assets/site.css"></head><body>')


def card(p: dict, t: dict) -> str:
    v = p.get("kind") in VERTICAL
    prev = (f'<video src="{e(p["preview"])}" controls playsinline preload="metadata"></video>' if p.get("preview")
            else '<div class="ph"></div>')
    cap = (f'<p class="cap">{e(p["caption"])}</p><button class="copy" data-t="{e(p["caption"])}">{t["copy"]}</button>'
           if p.get("caption") else "")
    dl = f'<a class="dl" href="{e(p["download"])}" target="_blank" rel="noopener">{t["download"]}</a>' if p.get("download") else ""
    return (f'<article class="card{" v" if v else ""}">{prev}<div class="meta"><span class="kind">'
            f'{e(t["kinds"].get(p.get("kind", ""), p.get("kind", "")))}</span><h3>{e(p["title"])}</h3>{cap}{dl}</div></article>')


SCRIPT = ("<script>document.querySelectorAll('.copy').forEach(b=>b.onclick=()=>{navigator.clipboard.writeText(b.dataset.t);"
          "const o=b.textContent;b.textContent=b.dataset.ok;setTimeout(()=>b.textContent=o,1500)})</script>")


def guest_page(data: dict, g: dict, t: dict) -> str:
    cards = "".join(card(p, t) for p in g.get("pieces", []))
    tr = (f'<p><a class="dl" href="{e(g["transcript"])}" target="_blank" rel="noopener">{t["transcript"]}</a></p>'
          if g.get("transcript") else "")
    return (head(f'{g["name"]} · {data["show"]}', data.get("lang", "en")) +
            f'<main class="wrap"><p class="show">{e(data["show"])}</p><h1>{e(g["name"])}</h1>'
            f'<p class="sub">{e(g.get("session", ""))}</p>{tr}<div class="grid">{cards}</div></main>' +
            SCRIPT.replace("b.dataset.ok", repr(t["copied"])) + "</body></html>")


def build(data: dict, out: Path) -> None:
    t = T.get(data.get("lang", "en"), T["en"])
    lang = data.get("lang", "en")
    for g in data["guests"]:
        if not SLUG.match(g["slug"]) or g["slug"] == "owner":
            raise ValueError(f"bad slug: {g['slug']!r} (use lower case letters, numbers and dashes)")
    (out / "entrar").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(head(data["show"], lang) + f'<main class="wrap center"><h1>{e(data["show"])}</h1>'
                                    f'<p class="sub">{t["private"]}</p></main></body></html>')
    (out / "entrar/index.html").write_text(
        head(t["enter"], lang) + f'<main class="wrap center"><h1>{e(data["show"])}</h1>'
        f'<form method="post" action="/entrar/" class="login"><input type="hidden" name="page" id="page">'
        f'<label>{t["password"]}<input name="password" type="password" autocomplete="current-password" required autofocus></label>'
        f'<p class="err" id="err" hidden>{t["wrong"]}</p><button>{t["enter"]}</button></form></main>'
        "<script>const q=new URLSearchParams(location.search);document.getElementById('page').value=q.get('page')||'';"
        "if(q.get('e'))document.getElementById('err').hidden=false</script></body></html>")
    for g in data["guests"]:
        d = out / "g" / g["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(guest_page(data, g, t))


if __name__ == "__main__":
    data = json.loads((HERE / "guests.json").read_text())
    build(data, HERE / "public")
    print(f"built {len(data['guests'])} guest page(s)")
