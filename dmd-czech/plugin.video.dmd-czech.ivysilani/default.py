# -*- coding: utf-8 -*-
import urllib2, urllib, re, os, time, datetime
from parseutils import *
from urlparse import urlparse,urlunparse
from util import addDir, addLink, addSearch, getSearch
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK
#import json
import simplejson as json
import httplib
import xml.etree.ElementTree as ET

def substr(data,start,end):
        i1 = data.find(start)
        i2 = data.find(end,i1)
        return data[i1:i2]

def substrAll(data,start,end):
        result = ''
        i1 = data.find(start)
        i2 = data.find(end,i1)
        result +=data[i1:i2]

        i1 = data.find(start,i2+1)
        while i1 >= 0:
                i2 = data.find(end,i1+1)
                result +=data[i1:i2]
                i1 = data.find(start, i2 + 1)

        return result



__baseurl__ = 'http://www.ceskatelevize.cz/ivysilani'
#__dmdbase__ = 'http://iamm.netuje.cz/xbmc/stream/'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
#swfurl = 'http://img8.ceskatelevize.cz/libraries/player/flashPlayer.swf?version=1.43'
swfurl = 'http://img.ceskatelevize.cz/libraries/player/flashPlayer.swf?version=1.45.5'
__settings__ = ArchivCZSK.get_addon('plugin.video.dmd-czech.ivysilani')
home = __settings__.get_info('path')
icon = os.path.join(home, 'icon.png')
search = os.path.join( home, 'search.png' )
nexticon = os.path.join(home, 'nextpage.png')
page_pole_url = []
page_pole_no = []
bonus_video = __settings__.get_setting('bonus-video')

DATE_FORMAT = '%d.%m.%Y'
DAY_NAME = (u'Po', u'Út', u'St', u'Čt', u'Pá', u'So', u'Ne')

RE_DATE   = re.compile('(\d{1,2}\.\s*\d{1,2}\.\s*\d{4})')


def OBSAH():
    addDir('Nejnovější pořady',__baseurl__+'/?nejnovejsi=vsechny-porady',12,icon)
    addDir('Nejsledovanější videa týdne',__baseurl__+'/?nejsledovanejsi=tyden',11,icon)
    addDir('Podle data',__baseurl__+'/podle-data-vysilani/',5,icon)
    addDir('Podle abecedy',__baseurl__+'/podle-abecedy/',2,icon)
    addDir('Podle kategorie',__baseurl__,1,icon)
    addDir('Vyhledat...(beta)','0',13,search)
    addDir('Živé iVysílání',__baseurl__+'/ajax/live-box?dc=',4,icon)

def KATEGORIE():
    addDir('Filmy',__baseurl__+'/filmy/',3,icon)
    addDir('Seriály',__baseurl__+'/serialy/',3,icon)
    addDir('Dokumenty',__baseurl__+'/dokumenty/',3,icon)
    addDir('Sport',__baseurl__+'/sportovni/',3,icon)
    addDir('Hudba',__baseurl__+'/hudebni/',3,icon)
    addDir('Zábava',__baseurl__+'/zabavne/',3,icon)
    addDir('Děti a mládež',__baseurl__+'/deti/',3,icon)
    addDir('Vzdělání',__baseurl__+'/vzdelavaci/',3,icon)
    addDir('Zpravodajství',__baseurl__+'/zpravodajske/',3,icon)
    addDir('Publicistika',__baseurl__+'/publicisticke/',3,icon)
    addDir('Magazíny',__baseurl__+'/magaziny/',3,icon)
    addDir('Náboženské',__baseurl__+'/nabozenske/',3,icon)
    addDir('Všechny',__baseurl__+'/zanr-vse/',3,icon)

def LIVE_OBSAH(url):
    url = url+str(time.time())
    #seznam kanalu a jejich id pro zive vysilani
    cas = datetime.datetime.now()
    cas = cas.hour
    #Decko a Art se stridaji, proto menim podle casu
    if(cas < 20 and cas >= 6):
        programctda = r'ČT:Déčko - '
        programctdaid = r'CT5'
    else:
        programctda = r'ČT ART - '
        programctdaid = r'CT6'
    program=[r'ČT1 - ', r'ČT2 - ', r'ČT24 - ', r'ČT4 - ', programctda, r' ', r' ', r' ', r' ', r' ', r' ', r' ', r' ']
    programid=[r'CT1', r'CT2', r'CT24', r'CT4', programctdaid, r'CT26', r'CT27', r'CT28', r'CT29', r'CT30', r'CT31', r'CT32', r'CT33']

    i = 0
    # Zjisteni hashe
    hashurl = 'http://www.ceskatelevize.cz/ct24/zive-vysilani/'
    req = urllib2.Request(hashurl)
    req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    httpdata = response.read()
    link=response.read()
    response.close()
    match = re.compile('hash=(.+?)&').findall(httpdata)
    hash = match[0]
    print 'HASH :'+hash
    
    i = 0
    request = urllib2.Request(url)
    request.add_header("Referer",__baseurl__)    
    request.add_header("Origin","http://www.ceskatelevize.cz")
    request.add_header("Accept","*/*")
    request.add_header("X-Requested-With","XMLHttpRequest")
    request.add_header("x-addr","127.0.0.1")
    request.add_header("User-Agent",_UserAgent_)
    request.add_header("Content-Type","application/x-www-form-urlencoded")
    con = urllib2.urlopen(request)
    # Read lisk XML page
    data = con.read()
    con.close()
    doc = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

    items = doc.find('div', 'clearfix')
    for item in items.findAll('div', 'channel'):
            prehrano = item.find('div','progressBar')
            prehrano = prehrano['style']
            prehrano = prehrano[(prehrano.find('width:') + len('width:') + 1):]
            #name_a = item.find('p')
            try:
                name_a = item.find('a') 
                name = program[i]+name_a.getText(" ").encode('utf-8')+'- Přehráno: '+prehrano.encode('utf-8')
                url = 'http://www.ceskatelevize.cz/ivysilani/embed/iFramePlayerCT24.php?hash='+hash+'&videoID='+programid[i]
                thumb = str(item.img['src'])
            except:
                name = program[i]+'Právě teď běží pořad, který nemůžeme vysílat po internetu.'
                thumb = 'http://img7.ceskatelevize.cz/ivysilani/gfx/empty/noLive.png'
            #print name, thumb, url
            addDir(name,url,14,thumb)
            i=i+1

def ABC(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    match = re.compile('<a class=\"pageLoadAjaxAlphabet\"\s*href=\"([^\"]+)\"\s*rel=\"letter=.+?\">\s+<span>([^<]+)</span>\s+</a>').findall(httpdata)
    for link,name in match:
        print name,__baseurl__+link
        addDir(name,'http://www.ceskatelevize.cz'+link,3,icon)

def CAT_LIST(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()

    cat_iter_regex = '<li>\s+?<a\s*?(title=\"(?P<desc>[^\"]+)\"){0,1}.+?href=\"(?P<url>[^\"]+)/\">(?P<title>[^<]+)<(.+?)</li>'
    httpdata = httpdata[httpdata.find('clearfix programmesList'):]
    for m in re.finditer(cat_iter_regex, httpdata, re.DOTALL):
        link = m.group('url')
        desc = m.group('desc')
        name = m.group('title')
        if m.group('url').find('labelBonus') != -1:
            name = name + ' (pouze bonusy)'
            if not bonus_video:
                continue
        infoLabels = {'title':name, 'plot':desc}
        #print name,link
        addDir(name, 'http://www.ceskatelevize.cz' + link, 6, icon, infoLabels=infoLabels)


# =============================================

# vypis CT1,CT2,CT24,CT4
def DAY_LIST(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    data = substr(httpdata,'data-type="actual-channels"','.columns.actual-channels')
    match = re.compile('<img src="(.+?)" alt="(.+?)"').findall(data)
    for item in match:
            addDir(item[1],url,9,item[0])



def DAY_PROGRAM_LIST( url, chnum ):
    nazvy=['ČT1', 'ČT2', 'ČT24', 'ČT sport', 'ČT:D', 'ČT art']
    nlink=['ct1', 'ct2', 'ct24', 'sport', 'dart', 'dart' ]
    index = nazvy.index(chnum)
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    data = substrAll(data,'programme-list channel-'+nlink[index]+'"','</ul')
    pattern = '<a href="(.+?)" class="program-item" title=[^>]+>[\s]*?<span class="time">(.+?)</span>[\s]*?<span class="title">(.+?)</span>'
    match = re.compile(pattern).findall(data)
    for item in match:
            addDir(item[1]+' '+item[2],'http://www.ceskatelevize.cz'+item[0],10,icon)

def date2label(date):
     dayname = DAY_NAME[date.weekday()]
     return "%s %s.%s.%s" % (dayname, date.day, date.month, date.year)


def DATE_LIST(url):
     pole_url = url.split("/")
     date = pole_url[len(pole_url) - 1]
     if date:
         date = datetime.date(*time.strptime(date, DATE_FORMAT)[:3])
     else:
         date = datetime.date.today()
     # Add link to previous month virtual folder
     pdate = date - datetime.timedelta(days=30)
     addDir('Předchozí měsíc (%s)' % date2label(pdate).encode('utf-8'), __baseurl__ + '/' + pdate.strftime(DATE_FORMAT), 5, icon)
     for i in range(0, 30):
           pdate = date - datetime.timedelta(i)
           addDir(date2label(pdate).encode('utf-8'), __baseurl__ + '/' + pdate.strftime(DATE_FORMAT), 8, icon)


# vypis nejsledovanejsi za tyden
def MOSTVISITED(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    data = substr(data,'<ul id="mostWatchedBox"','</div>')
    pattern = '<a href="(.+?)">[\s]*?<img src="(.+?)".*?>[\s]*?(.+?)</a'
    match = re.compile(pattern).findall(data)
    for item in match:
        addDir(item[2].strip().replace('<br />',' '),'http://www.ceskatelevize.cz'+item[0],10,item[1])
        

def NEWEST(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    data = substr(data,'<ul id="newestBox"','</div>')
    pattern = '<a href="(.+?)">[\s]*?<img src="(.+?)".*?>[\s]*?(.+?)</a'
    match = re.compile(pattern).findall(data)
    for item in match:
        addDir(item[2].strip().replace('<br />',' '),'http://www.ceskatelevize.cz'+item[0],10,item[1])


# =============================================


def VIDEO_LIST(url, video_listing= -1):
    program_single_start = '<div id="programmeInfoDetlail">'
    program_single_end = '<div id="programmePlayer">'
    program_multi_start = '<div id="programmeMoreBox" class="clearfix">'
    program_multi_end = '<div id="programmeRelated">'
    single_regex = '<a href=\"(?P<url>[^"]+).*?<h2>(?P<title>[^<]+)<\/h2>.*?<p>(?P<desc>[^<]+)<\/p>'
    iter_regex = '<li class=\"itemBlock (clearfix|clearfix active).*?<a class=\"itemImage\".*?src=\"(?P<img>[^"]+).*?<a class=\"itemSetPaging\".*?href=\"(?P<url>[^"]*).+?>(?P<title>[^<]+).*?<\/li>'
    paging_regex = '<div\s*id=\"paginationControl.+?<span class=\"selected\">(?P<page>[^<]+)</span>.+?<a href=\"(?P<nexturl>[^\"]+)\".+?class=\"next\".+?</a>.+?</div>'

    link = url
    if not re.search('/dalsi-casti', url):
        m = re.search('http://www.ceskatelevize.cz/ivysilani/([^/]+)/[\w,-]+', url)
        if m:
            url = url[:m.end(1)]
    req = urllib2.Request(link)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    #doc = read_page(link)
    if re.search('Bonusy', str(httpdata), re.U) and video_listing == -1:
        bonuslink = url + 'bonusy/'
        if re.search('dalsi-casti', url):
            bonusurl = re.compile('(.+?)dalsi-casti/?').findall(url)
            bonuslink = bonusurl[0] + 'bonusy/'
        addDir('Bonusy', bonuslink, 7, nexticon)
        print 'Bonusy = True - ' + url + 'bonusy/'
    #items = doc.find('ul', 'clearfix content')
    if re.search('Ouha', httpdata, re.U):
        bonuslink = url + 'bonusy/'
        BONUSY(bonuslink)


    item_single = True

    multidata = httpdata[httpdata.find(program_multi_start):httpdata.find(program_multi_end)]
    items = re.compile(iter_regex, re.DOTALL).finditer(multidata)

    for item in items:
        item_single = False
        thumb = item.group('img')
        name = item.group('title').strip()
        url = 'http://www.ceskatelevize.cz' + item.group('url')
        url = re.sub('porady', 'ivysilani', url)
        print item.group('url'), item.group('title').strip()
        addDir(name, url, 10, thumb)

    if item_single:
        program_single_start = '<div id="programmeInfoDetail">'
        program_single_end = 'div id="programmePlayer">'
        singledata = httpdata[httpdata.find(program_single_start):httpdata.find(program_single_end)]
        #print singledata
        item = re.search(single_regex, singledata, re.DOTALL)
        #print item.group('url'), item.group('title').strip(), item.group('desc')

        name = item.group('title').strip()
        popis = item.group('desc')
        url = 'http://www.ceskatelevize.cz' + item.group('url')
        url = re.sub('porady', 'ivysilani', url)
        infoLabels = {'title':name, 'plot':popis}
        addDir(name, url, 10, None, infoLabels=infoLabels)

    try:
        pager = re.search(paging_regex, multidata, re.DOTALL)
        act_page = int(pager.group('page'))
        #print act_page,next_page_i
        next_url = pager.group('nexturl')
        next_label = '>> Další strana >>'
        #print next_label,next_url

        video_listing_setting = int(__settings__.get_setting('video-listing'))
        if video_listing_setting > 0:
            next_label = '>> Další strany >>'
        if (video_listing_setting > 0 and video_listing == -1):
                if video_listing_setting == 3:
                        video_listing = 99999
                elif video_listing_setting == 2:
                        video_listing = 3
                else:
                        video_listing = video_listing_setting
        if (video_listing_setting > 0 and video_listing > 0):
                VIDEO_LIST('http://ceskatelevize.cz' + next_url, video_listing - 1)
        else:
                print next_label, 'http://www.ceskatelevize.cz' + next_url
                addDir(next_label, 'http://www.ceskatelevize.cz' + next_url, 6, nexticon)
    except Exception as e:
        print e
        print 'STRANKOVANI NENALEZENO!'

def BONUSY(link):
    doc = read_page(link)
    items = doc.find('ul', 'clearfix content')
    if re.search('Ouha', str(items), re.U):
        link = url + 'bonusy/'
        BONUSY(link)
    for item in items.findAll('li', 'itemBlock clearfix'):
        name_a = item.find('h3')
        name_a = name_a.find('a')
        name = name_a.getText(" ").encode('utf-8')
        if len(name) < 2:
            name = 'Titul bez názvu'
        url = 'http://www.ceskatelevize.cz' + str(item.a['href'])
        url = re.sub('porady', 'ivysilani', url)
        thumb = str(item.img['src'])
        #print name, thumb, url
        addDir(name, url, 10, thumb)
    try:
        pager = doc.find('div', 'pagingContent')
        act_page_a = pager.find('td', 'center')
        act_page = act_page_a.getText(" ").encode('utf-8')
        act_page = act_page.split()
        next_page_i = pager.find('td', 'right')
        #print act_page,next_page_i
        next_url = next_page_i.a['href']
        next_label = 'Další strana (Zobrazena videa ' + act_page[0] + '-' + act_page[2] + ' ze ' + act_page[4] + ')'
        #print next_label,next_url
        addDir(next_label, 'http://www.ceskatelevize.cz' + next_url, 7, nexticon)
    except:
        print 'STRANKOVANI NENALEZENO!'


def HLEDAT(url):
    #https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=20&hl=cs&prettyPrint=false&source=gcsc&gss=.cz&sig=981037b0e11ff304c7b2bfd67d56a506&cx=000499866030418304096:fg4vt0wcjv0&q=vypravej+tv&googlehost=www.google.com&callback=google.search.Search.apiary6680&nocache=1360011801862
    #https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=20&start=20&hl=cs&prettyPrint=false&source=gcsc&gss=.cz&sig=981037b0e11ff304c7b2bfd67d56a506&cx=000499866030418304096:fg4vt0wcjv0&q=vypravej+tv&googlehost=www.google.com&callback=google.search.Search.apiary6680&nocache=1360011801862
    if url == '0':
            what = getSearch(session)
            if not what == '':
                what = re.sub(' ', '+', what)
                url2 = 'https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=20&hl=cs&prettyPrint=false&source=gcsc&gss=.cz&sig=981037b0e11ff304c7b2bfd67d56a506&cx=000499866030418304096:fg4vt0wcjv0&q=' + what + '&googlehost=www.google.com&callback=google.search.Search.apiary6680&nocache=1360011801862'
    else:
        match_page = re.compile('start=([0-9]+)').findall(url)
        match2 = re.compile('q=(.+?)&googlehost').findall(url)
        next_page = int(match_page[0]) + 20
        url2 = url
    req = urllib2.Request(url2)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    match = re.compile('google.search.Search.apiary6680\((.*)\)').findall(httpdata)
    items = json.loads(match[0])[u'results']
    for item in items:
        print item
        name = item[u'titleNoFormatting']
        name = name.encode('utf-8')
        url2 = item[u'url']
        try:
            image = item[u'richSnippet'][u'cseImage'][u'src']
            image = image.encode('utf-8')
        except:
            image = icon
        if re.search('diskuse', url2, re.U):
            continue
        #if not re.search('([0-9]{15}-)', url, re.U):
        #continue
        addDir(name, url2, 10, image)
    if url == '0':
        next_url = 'https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=20&start=20&hl=cs&prettyPrint=false&source=gcsc&gss=.cz&sig=981037b0e11ff304c7b2bfd67d56a506&cx=000499866030418304096:fg4vt0wcjv0&q=' + what + '&googlehost=www.google.com&callback=google.search.Search.apiary6680&nocache=1360011801862'
        next_title = '>> Další strana (výsledky 0 - 20)'
        addDir(next_title, next_url, 13, nexticon)
    else:
        next_url = 'https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=20&start=' + str(next_page) + '&hl=cs&prettyPrint=false&source=gcsc&gss=.cz&sig=981037b0e11ff304c7b2bfd67d56a506&cx=000499866030418304096:fg4vt0wcjv0&q=' + match2[0] + '&googlehost=www.google.com&callback=google.search.Search.apiary6680&nocache=1360011801862'
        next_title = '>> Další strana (výsledky ' + str(match_page[0]) + ' - ' + str(next_page) + ')'
        addDir(next_title, next_url, 13, nexticon)



def VIDEOLINK(url,name, live):
    if name.find('pořad se ještě nevysílá')!=-1:
            return

    ### Log URL
    url_path = url.replace('http://www.ceskatelevize.cz', '')
    print '====> URL: '+ url
    print '====> URL Path: '+ url_path

    ### HTTP Connection to www.ceskatekevize.cz
    conn = httplib.HTTPConnection('www.ceskatelevize.cz')

    ### Load main page
    headers = {
       'User-Agent': _UserAgent_
    }
    conn.request('GET', url_path, '', headers)
    res = conn.getresponse()
    httpdata = res.read();

    #print '====> MAIN PAGE START: ' + url
    #print httpdata
    #print '====> MAIN PAGE END: ' + url

    ### Extract Info from main page
    info = re.compile('<title>(.+?)</title>').findall(httpdata)
    info = info[0]
    if (name == ''):
        name = info
    print '====> Title: ' + info

    ### Extract Playlist ID form main page
    playlist = re.search('getPlaylistUrl.+?type":"(.+?)","id":"(.+?)"', httpdata, re.DOTALL)
    playlist_type = playlist.group(1)
    playlist_id = playlist.group(2)

    print '====> Playlist ID: ' + playlist_id

    ### Get Playlist link
    headers = {
       'Connection': 'keep-alive',
       'x-addr': '127.0.0.1',
       'User-Agent': _UserAgent_,
       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
       'Accept': '*/*',
       'X-Requested-With': 'XMLHttpRequest',
       'Referer': url,
       'Origin': 'http://www.ceskatelevize.cz'
    }
    data = {
       'playlist[0][type]' : playlist_type,
       'playlist[0][id]' : playlist_id,
       'requestUrl' : url_path,
       'requestSource' : 'iVysilani'
    }
    conn.request('POST', '/ivysilani/ajax/get-playlist-url', urllib.urlencode(data), headers )
    res = conn.getresponse()
    httpdata = res.read()
    conn.close()

    #print '====> PLAYLIST LINK PAGE START'
    #print httpdata
    #print '====> PLAYLIST LINK PAGE END'

    ### Extract Playlist URL
    jsondata = json.loads(httpdata);
    playlist_url = urllib.unquote(jsondata['url'])

    print '====> Playlist ULR: ' + playlist_url
    urlobj = urlparse(playlist_url)
    urlhost = urlobj.netloc
    urlpath = urlunparse(('', '', urlobj.path, urlobj.params, urlobj.query, urlobj.fragment))

    print '===> Playlist Host= ' + urlhost + ' Path=' + urlpath

    ### Get Playlists
    conn = httplib.HTTPConnection(urlhost)
    headers = {
       'Connection': 'keep-alive',
       #'Referer': 'http://imgct.ceskatelevize.cz/global/swf/player/player.swf?version=1.45.15a',
       'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36',
       'Accept-Encoding': 'identity',
       #'Accept-Encoding': 'gzip,deflate,sdch',
       'Accept-Language': 'en-US,en;q=0.8,cs;q=0.6'
    }
    conn.request('GET', urlpath, '', headers)
    res = conn.getresponse()
    httpdata = res.read()
    conn.close()

    #print '====> PLAYLIST PAGE START'
    #print httpdata
    #print '====> PLAYLIST PAGE END'

    ### Read links XML page
    httpdata = urllib2.unquote(httpdata)
    root = ET.fromstring(httpdata)
    for item in root.findall('.//body/switchItem'):
        if ('id' in item.attrib) and ('base' in item.attrib):
            id = item.attrib['id']
            base = item.attrib['base']

            if re.search('AD', id, re.U):
                continue

            base = re.sub('&amp;','&', base)

            print '==> SwitchItem id=' + id + ', base=' + base

            for videoNode in item.findall('./video'):
                if ('src' in videoNode.attrib) and ('label' in videoNode.attrib):
                        src = videoNode.attrib['src']
                        label = videoNode.attrib['label']
                        if live:
                            rtmp_url = base+'/'+src
                        else:
                            app = base[base.find('/', base.find('://') + 3) + 1:]
                            rtmp_url = base + ' app=' + app + ' playpath=' + src
                        print 'RTMP label=' + label + ', name=' + name + ', url=' + rtmp_url
                        addLink(label+' '+name, rtmp_url, icon, info)


def http_build_query(params, topkey=''):
    from urllib import quote_plus

    if len(params) == 0:
       return ""

    result = ""

    # is a dictionary?
    if type (params) is dict:
       for key in params.keys():
           newkey = quote_plus (key)

           if topkey != '':
              newkey = topkey + quote_plus('[' + key + ']')

           if type(params[key]) is dict:
              result += http_build_query (params[key], newkey)

           elif type(params[key]) is list:
                i = 0
                for val in params[key]:
                    if type(val) is dict:
                       result += http_build_query (val, newkey + '[' + str(i) + ']')

                    else:
                       result += newkey + quote_plus('[' + str(i) + ']') + "=" + quote_plus(str(val)) + "&"

                    i = i + 1

           # boolean should have special treatment as well
           elif type(params[key]) is bool:
                result += newkey + "=" + quote_plus(str(int(params[key]))) + "&"

           # assume string (integers and floats work well)
           else:
                try:
                  result += newkey + "=" + quote_plus(str(params[key])) + "&"       # OPRAVIT ... POKUD JDOU U params[key] ZNAKY > 128, JE ERROR, ALE FUNGUJE TO I TAK
                except:
                  result += newkey + "=" + quote_plus("") + "&"

    # remove the last '&'
    if (result) and (topkey == '') and (result[-1] == '&'):
       result = result[:-1]

    return result


url = None
name = None
thumb = None
mode = None

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass


print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)


if mode == None or url == None or len(url) < 1:
        print ""
        OBSAH()

elif mode == 1:
        print ""
        KATEGORIE()

elif mode == 2:
        print "" + url
        ABC(url)

elif mode == 3:
        print "" + url
        CAT_LIST(url)

elif mode == 4:
        print "" + url
        LIVE_OBSAH(url)

elif mode == 5:
        print "" + url
        DATE_LIST(url)

elif mode == 6:
        print "" + url
        VIDEO_LIST(url)

elif mode == 7:
        print "" + url
        BONUSY(url)

elif mode == 8:
        print "" + url
        DAY_LIST(url)

elif mode == 9:
        print "" + url
        DAY_PROGRAM_LIST(url, name)

elif mode == 10:
        print "" + url
        VIDEOLINK(url, name, False)

elif mode == 11:
        print "" + url
        MOSTVISITED(url)

elif mode == 12:
        print "" + url
        NEWEST(url)

elif mode == 13:
        print "" + url
        HLEDAT(url)

elif mode == 14:
        print "" + url
        VIDEOLINK(url, name, True)
