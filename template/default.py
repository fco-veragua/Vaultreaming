import xbmcplugin
import xbmcgui
import sys

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')

list_item = xbmcgui.ListItem(label="¡Hola, Vaultreaming!")
xbmcplugin.addDirectoryItem(handle=addon_handle, url="", listitem=list_item, isFolder=False)

xbmcplugin.endOfDirectory(addon_handle)
