# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparse
from BeautifulSoup import BeautifulSoup
import time, datetime
import HTMLParser

#todo: BeautifulSoup

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - cda.pl"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join(ptv.getAddonInfo('path'), "../resources")
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser
from search import Search

log = mrknow_pLog.pLog()

mainUrl = 'http://www.cda.pl/'
mainUrlb = 'http://www.cda.pl'
movies = 'http://www.cda.pl/video/show/ca%C5%82e_filmy_or_ca%C5%82y_film_or_lektor_or_dubbing_or_napisy/p1'

HOST = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36'

MENU_TAB = {1: "Filmy najtrafniejsze",
            2: "Filmy najwyżej ocenione",
            3: "Filmy popularne",
            4: "Filmy najnowsze",
            5: "Filmy alfabetycznie",
            6: "Najnowsze",
            7: "Video najpopularniejsze na FB",
            8: "Video najlepiej ocenione",
            9: "Krótkie filmy i animacje",
            10: "Filmy Extremalne",
            11: "Motoryzacja, wypadki",
            12: "Muzyka",
            13: "Prosto z Polski",
            14: "Rozrywka",
            15: "Różności",
            16: "Sport",
            17: "Śmieszne filmy",
            27: "Szukaj"}

PREM = {
    "http://www.cda.pl/premium/akcji": "Akcja",
    "http://www.cda.pl/premium/dramaty": "Dramaty",
    "http://www.cda.pl/premium/familijne": "Familijne",
    "http://www.cda.pl/premium/fantasy": "Fantasy",
    "http://www.cda.pl/premium/historyczne": "Historyczne",
    "http://www.cda.pl/premium/horror": "Horror",
    "http://www.cda.pl/premium/komedie": "Komedie",
    "http://www.cda.pl/premium/kryminalne": "Kryminalne",
    "http://www.cda.pl/premium/muzyczne": "Muzyczne",
    "http://www.cda.pl/premium/obyczajowe": "Obyczajowe",
    "http://www.cda.pl/premium/polskie": "Polskie",
    "http://www.cda.pl/premium/przygodowe": "Przygodowe",
    "http://www.cda.pl/premium/psychologiczne": "Psychologiczne",
    "http://www.cda.pl/premium/romanse": "Romanse",
    "http://www.cda.pl/premium/sci-fi": "Sci-fi",
    "http://www.cda.pl/premium/sensacyjne": "Sensacyjne",
    # "http://www.cda.pl/premium/seriale-i-miniserie"" : "Seriale i Miniserie",
    "http://www.cda.pl/premium/thrillery": "Thrillery",
    "http://www.cda.pl/premium/wojenne": "Wojenne"
}
max_stron = 0


class cdapl(object):
    def __init__(self):
        log.info('Starting cdapl.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        # self.up = urlparser.urlparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self._addon = xbmcaddon.Addon()
        self.COOKIEFILE = xbmc.translatePath('special://profile/addon_data/%s/cookies/cdapl.cookie' %
                                             self._addon.getAddonInfo('id'))
        self.search = Search(url='http://www.cda.pl/video/show/%(quoted)s/p1?s=best',
                             service='cdapl', listItemsFun=self.listsItems)

    def listsMainMenu(self, table):
        self.premium = self.up.CDA2isPremium()
        if self.premium == True:
            self.add('main-menu', '[COLOR yellow]PREMIUM[/COLOR]', folder=True, isPlayable=False)
        for num, val in table.items():
            self.add('main-menu', val, folder=True, isPlayable=False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsMainMenu2(self, table):
        table = sorted([(value, key) for (key, value) in table.items()])
        for num, val in table:
            log("Logujemy %s %s " % (num, val))
            self.add('main-menu2', num, num, None, val, folder=True, isPlayable=False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    #
    def listsItems3(self, url):
        query_data = {'url': url, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': True,
                      'load_cookie': True,
                      'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True}
        page = self.cm.getURLRequestData(query_data)

        for match in re.finditer(
            r'<span class="cover-area">\s*<a href="(.*?)(?:\?from=catalog)?"[^>]*\s+class="cover-big"[^>]*>.*?<img title="(.*?)"[^>]*\s+src="(.*?)"[^>]*>.*?</a>.*?<span[^>]*\s+class="cloud-gray"[^>]*>(.*?)</span>', page, re.DOTALL):
            log(match)
            url, title, image, variants = match.group(1, 2, 3, 4)
            self.add('playSelectedMovie', None,
                     self.cm.html_special_chars(title) + ' - ' + variants, image,
                     mainUrlb + url, folder=False, isPlayable=False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    #def listsCategoriesMenu(self, url):
    #    query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
    #    link = self.cm.getURLRequestData(query_data)
    #    # ile jest filmów ?
    #    match = re.compile(
    #        '<li class="active"id="mVid"><a href="#" onclick="moreVideo\(\);return false;">Video \((.*?)\)</a></li>',
    #        re.DOTALL).findall(link)
    #    ilejest = int(match[0])
    #    policz = int(ilejest / o_filmow_na_stronie) + 1
    #    max_stron = policz
    #    parsed = urlparse.urlparse(url)
    #    typ = urlparse.parse_qs(parsed.query)['s'][0]
    #    for i in range(0, (policz)):
    #        purl = 'http://www.cda.pl/video/show/ca%C5%82e_filmy_or_ca%C5%82y_film/p' + str(i + 1) + '?s=' + typ
    #        self.add('categories-menu', 'Strona ' + str(i + 1), url=purl, folder=True, isPlayable=False,
    #                 strona=str(i + 1))
    #    xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def date_to_millis(self, typ=0):
        d = datetime.datetime.utcnow()
        if typ == 1:
            return str(int(time.mktime(d.timetuple())) * 10)
        return str(int(time.mktime(d.timetuple())) * 1000)

    def listsItems(self, url):
        self.premium = self.up.CDA2isPremium()

        query_data = {'url': url, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': True,
                      'load_cookie': True,
                      'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost1 = soup.find('div', {"id": "dodane_video"})
        linki_all1 = linki_ost1.findAll('label') if linki_ost1 else ()
        for mylink in linki_all1:
            try:
                #log.info('A1 %s' % mylink.a)
                log.info('A2 %s' % mylink.a.img)

                #log.info('AA2 %s %s' % mylink.a.img['alt'], mylink.a.img['src'])
                mytext = ''
                hd = mylink.find('span', {'class': 'hd-ico-elem hd-elem-pos'})
                prem = mylink.find('span', {'class': 'flag-video-premium'})
                if hd:
                    log.info('cda.pl %s' % hd.text)
                    if hd.text == '1080p':
                        mytext = '[[COLOR yellow]' + hd.text + '[/COLOR]] - '
                    elif hd.text == '720p':
                        mytext = '[[COLOR green]' + hd.text + '[/COLOR]] - '
                    else:
                        mytext = '[' + hd.text + '] - '
                if prem:
                    mytext = mytext + '[COLOR yellow]PREMIUM[/COLOR] '

                    if self.premium:
                        self.add('playSelectedMovie', None, mytext + mylink.a.img['alt'], 'http:'+ mylink.a.img['src'],
                                 mainUrlb + mylink.a['href'], folder=False, isPlayable=False)
                    else:
                        self.add('playSelectedMovie', None, mytext + mylink.a.img['alt'], 'http:'+ mylink.a.img['src'],
                                 folder=False, isPlayable=False)
                else:
                    self.add('playSelectedMovie', None, mytext + mylink.a.img['alt'], 'http:'+ mylink.a.img['src'],
                             mainUrlb + mylink.a['href'], folder=False, isPlayable=False)
            except:
                pass

        match10 = re.compile(
            '<span class="next-wrapper"><a class="sbmBigNext btn-my btn-large fiximg" href="(.*?)" onclick="(.*?)">\n<span class="hide-loader btn-loader-lft">',
            re.DOTALL).findall(link)
        if match10:
            myurl = mainUrlb + urllib.quote(match10[0][0])
            self.add('categories-menu', 'Następna strona', url=myurl, folder=True, isPlayable=False,
                     strona=myurl)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems2(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost1 = soup.find('div', {"class": "rigthWrapColumn"})
        linki_all1 = linki_ost1.findAll('div', {'class': 'videoElem'}) if linki_ost1 else ()
        for mylink in linki_all1:
            # print("m",mylink.a.text,mylink.a['href'])
            mytext = ''
            hd = mylink.find('span', {'class': 'hd-ico-elem hd-elem-pos'})
            if hd:
                log.info('cda.pl %s' % hd.text)
                if hd.text == '1080p':
                    mytext = '[[COLOR yellow]' + hd.text + '[/COLOR]] - '
                elif hd.text == '720p':
                    mytext = '[[COLOR green]' + hd.text + '[/COLOR]] - '
                else:
                    mytext = '[' + hd.text + '] - '
            self.add('playSelectedMovie', None, mytext + mylink.a['alt'], mylink.a.img['src'],
                     mainUrlb + mylink.a['href'], folder=False, isPlayable=False)

        match10 = re.compile(
            '<span class="next-wrapper"><a class="sbmBigNext btn-my btn-large fiximg" href="(.*?)" onclick="(.*?)">\n<span class="hide-loader btn-loader-lft">',
            re.DOTALL).findall(link)
        if match10:
            myurl = mainUrlb + urllib.quote(match10[0][0])
            self.add('main-menu', 'Następna strona', url=myurl, folder=True, isPlayable=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def getMovieLinkFromXML(self, url):
        options = ""
        if ptv.getSetting('cda_show_rate') == 'true':
            options = 'bitrate'
        return self.up.getVideoLink(url, "", options)

    def add(self, name, category=None, title=None, iconimage=None, url=None, desc=None, rating=None,
            folder=True, isPlayable=True, strona='', service=None):
        # TODO: someting with unused arguments "descr", "rating"
        if not service:    service = 'cdapl'
        if not category:   category = 'NONE'
        if not title:      title = 'NONE'
        if not iconimage:  iconimage = 'NONE'
        if not url:        url = 'NONE'
        title = HTMLParser.HTMLParser().unescape(title)
        u = sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + \
            "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + \
            urllib.quote_plus(iconimage) + "&strona=" + urllib.quote_plus(strona)
        # log.info(str(u))
        if name == 'main-menu' or name == 'categories-menu':
            title = category
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz = xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo(type="Video", infoLabels={"Title": title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=folder)

    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title, icon):
        ok = True
        mrknow_pCommon.mystat(videoUrl)
        log('moje url = %s' % videoUrl)
        if videoUrl == '':
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
            return False
        liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        liz.setInfo(type="Video", infoLabels={"Title": title, })
        try:
            xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(videoUrl, liz)

            if not xbmc.Player().isPlaying():
                xbmc.sleep(10000)
                # xbmcPlayer.play(url, liz)
        except:
            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu.', 'Problem')
        return ok

    def handleService(self):
        params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        strona = self.parser.getParam(params, "strona")
        print ("Dane", url, name, category, title)
        #log.info("Dane: url:%s, name:%s, category:%s, title=%s" % (url, name, category, title))
        if url is not None:
            log.info('[cda.pl] url:%s' % url)
        if name is None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == '[COLOR yellow]PREMIUM[/COLOR]':
            self.listsMainMenu2(PREM)
        elif name == 'main-menu2':
            self.listsItems3(url)

        elif name == 'main-menu' and category == 'Najnowsze':
            self.listsItems2('http://www.cda.pl/video/p1')
        elif name == 'main-menu' and category == 'Video najpopularniejsze na FB':
            self.listsItems2('http://www.cda.pl/video/p1?o=popular&k=miesiac')
        elif name == 'main-menu' and category == 'Video najlepiej ocenione':
            self.listsItems2('http://www.cda.pl/video/p1?o=top&k=miesiac')
        elif name == 'main-menu' and category == 'Krótkie filmy i animacje':
            self.listsItems2('http://www.cda.pl/video/kat26/p1')
        elif name == 'main-menu' and category == 'Filmy Extremalne':
            self.listsItems2('http://www.cda.pl/video/kat24/p1')
        elif name == 'main-menu' and category == 'Motoryzacja, wypadki':
            self.listsItems2('http://www.cda.pl/video/kat27/p1')
        elif name == 'main-menu' and category == 'Muzyka':
            self.listsItems2('http://www.cda.pl/video/kat28/p1')
        elif name == 'main-menu' and category == 'Prosto z Polski':
            self.listsItems2('http://www.cda.pl/video/kat29/p1')
        elif name == 'main-menu' and category == 'Rozrywka':
            self.listsItems2('http://www.cda.pl/video/kat30/p1')
        elif name == 'main-menu' and category == 'Różności':
            self.listsItems2('http://www.cda.pl/video/kat33/p1')
        elif name == 'main-menu' and category == 'Sport':
            self.listsItems2('http://www.cda.pl/video/kat31/p1')
        elif name == 'main-menu' and category == 'Śmieszne filmy':
            self.listsItems2('http://www.cda.pl/video/kat32/p1')
        elif name == 'main-menu' and category == 'Następna strona':
            self.listsItems2(url)

        elif name == 'main-menu' and category == 'Filmy najtrafniejsze':
            log.info('Jest Najtrafniejsze: ')
            self.listsItems(movies + '?s=best')
        elif name == 'main-menu' and category == 'Filmy najwyżej ocenione':
            log.info('Jest Najwyżej ocenione: ')
            self.listsItems(movies + '?s=rate')
        elif name == 'main-menu' and category == 'Filmy popularne':
            log.info('Jest Popularne: ')
            self.listsItems(movies + '?s=popular')
        elif name == 'main-menu' and category == 'Filmy najnowsze':
            log.info('Jest Najnowsze: ')
            # self.listsItems(movies +'s=date')
            self.listsItems(movies + '?duration=all&section=&quality=all&section=&s=date&section=')
        elif name == 'main-menu' and category == 'Filmy alfabetycznie':
            log.info('Jest Alfabetycznie: ')
            self.listsItems(movies + '?s=alf')
        elif self.search.handleService(force=(name == 'main-menu' and category == 'Szukaj')):
            return
        elif name == 'categories-menu' and category == 'filmy':
            log.info('url: ' + str(movies))
            self.listsItems(movies)
        elif name == 'categories-menu' and category != 'NONE':
            log.info('url: ' + str(url))
            log.info('strona: ' + str(strona))
            self.listsItems(url)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)


