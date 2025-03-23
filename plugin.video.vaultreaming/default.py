import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import sys
import urllib.parse
import urllib.request
import re
import os

BASE_URL = "https://www1.pelisforte.se" # Pelisforte

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')

def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": url,
        "Origin": "https://www1.pelisforte.se"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        xbmc.log(f"HTML received: {html[:5000]}", xbmc.LOGDEBUG) # TESTING:
    return html
    
def extract_movies(html):
    pattern = re.compile(r'<article class="item movies">.*?<h3>(.*?)</h3>.*?<a href="(.*?)"', re.DOTALL)
    return pattern.findall(html)

def show_main_menu():
    options = [
        ("Buscar por NOMBRE...", "search")
    ]

    for label, option in options:
        url = f'{sys.argv[0]}?action={option}'
        list_item = xbmcgui.ListItem(label=label)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

def search_movies(name):
    query = urllib.parse.quote(name)
    url = f'{BASE_URL}/?s={query}'

    html = get_html(url)

    xbmc.log(f"HTML received (partial): {html[:5000]}", xbmc.LOGDEBUG) # TESTING:

    ul_match = re.search(r'<ul[^>]*class\s*=\s*["\'][^"\']*post-lst[^"\']*["\'][^>]*>(.*?)</ul>', html, re.DOTALL)

    if not ul_match:
        xbmcgui.Dialog().ok("Error", "RESULTS NOT FOUND FOR THE SEARCH (UL)...")
        return
    else:
        xbmc.log("SEARCH CONTINUES FINE (UL)!...", xbmc.LOGDEBUG)
    
    ul_content = ul_match.group(1); xbmc.log(f"HTML (ul_content): {ul_content}", xbmc.LOGDEBUG) # TESTING: ESTÁ SACANDO CORRECTAMENTE EL ul_content, los <li>...

    movies = re.findall(
    r'<li[^>]*>.*?<h2[^>]*class=["\']?entry-title["\']?>(.*?)</h2>.*?<a[^>]*href=(["\']?)(https?://[^"\']+)\2[^>]*class=["\']?lnk-blk["\']?',
    ul_content,
    re.DOTALL
    )

    if not movies:
        xbmcgui.Dialog().ok("Error", "RESULTS NOT FOUND...")
        return

    for title, _, link in movies:
        list_item = xbmcgui.ListItem(label=title)
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, 
            url=f"{sys.argv[0]}?action=play&url={urllib.parse.quote(link)}",
            listitem=list_item, 
            isFolder=False
        )
    
    xbmcplugin.endOfDirectory(addon_handle)

def play_movie(url):
    html = get_html(url)

    regex_idiomas = re.findall(r'<span\s+tab=(ln\d+)[^>]*>([^<]+)</span>', html)

    if not regex_idiomas:
        xbmcgui.Dialog().ok("Error", "No se encontraron opciones de idioma.")
        return

    opciones_idioma = {id_lang: label.strip() for id_lang, label in regex_idiomas}
    
    xbmc.log(f"🔍 Idiomas detectados: {opciones_idioma}", xbmc.LOGDEBUG)

    idioma_keys = list(opciones_idioma.keys())
    idioma_labels = list(opciones_idioma.values())

    index = xbmcgui.Dialog().select("Selecciona el idioma", idioma_labels)
    if index == -1:
        return

    idioma_seleccionado = idioma_keys[index]
    xbmc.log(f"✅ Idioma seleccionado: {opciones_idioma[idioma_seleccionado]}", xbmc.LOGDEBUG)

    regex_opciones = fr'<div\s+id={idioma_seleccionado}[^>]*>.*?<ul\s+class=["\']aa-tbs aa-tbs-video["\'][^>]*>(.*?)</ul>'
    match = re.search(regex_opciones, html, re.DOTALL)

    if not match:
        xbmcgui.Dialog().ok("Error", "No se encontraron opciones de servidor.")
        return

    opciones_html = match.group(1)
    xbmc.log(f"🔍 Contenido de servidores para {opciones_idioma[idioma_seleccionado]}: {opciones_html}", xbmc.LOGDEBUG)

    opciones_servidor = re.findall(r'<a\s+class=["\']?btn.*?href=["\']?#(options-\d+)["\']?[^>]*>.*?<span\s+class=server>(.*?)</span>', opciones_html, re.DOTALL)

    if not opciones_servidor:
        xbmcgui.Dialog().ok("Error", "No se encontraron opciones de reproducción.")
        return

    servidor_keys = [opt[0] for opt in opciones_servidor]
    servidor_labels = [opt[1].strip() for opt in opciones_servidor]

    xbmc.log(f"🔍 Servidores detectados: {servidor_labels}", xbmc.LOGDEBUG)

    index = xbmcgui.Dialog().select("Selecciona el servidor", servidor_labels)
    if index == -1:
        return

    servidor_seleccionado = servidor_keys[index]
    xbmc.log(f"✅ Servidor seleccionado: {servidor_labels[index]}", xbmc.LOGDEBUG)

    regex_iframe = fr'<div\s+id={servidor_seleccionado}[^>]*>.*?<iframe[^>]+(?:data-src|src)=["\'](https?://[^"\']+)["\']'
    match_iframe = re.search(regex_iframe, html, re.DOTALL)

    if not match_iframe:
        xbmcgui.Dialog().ok("Error", "No se encontró el enlace de video.")
        return

    url_video = match_iframe.group(1)
    xbmc.log(f"🎬 Enlace de video encontrado: {url_video}", xbmc.LOGDEBUG)

    play_item = xbmcgui.ListItem(path=url_video)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

    play_item = xbmcgui.ListItem(path=url_video)

    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

    xbmc.sleep(2000)
    xbmc.Player().play(url_video, play_item)

def get_params():
    param_string = sys.argv[2][1:] if len(sys.argv) > 2 else ""
    return dict(urllib.parse.parse_qsl(param_string))

if __name__ == '__main__':
    params = get_params()
    action = params.get("action")

    if action is None:
        show_main_menu()
    elif action == "search":
        tec = xbmcgui.Dialog().input("Introduce el NOMBRE de la película...")
        if tec:
            search_movies(tec)
    elif action == "play":
        play_movie(params["url"])