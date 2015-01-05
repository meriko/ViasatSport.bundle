TITLE  = 'Viasat Sport'
PREFIX = '/video/viasatsport'

ART  = R('art-default.jpg')
ICON = R('icon-default.png')

BASE_URL = 'http://www.viasatsport.se'

HTTP_USER_AGENT = "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4"

####################################################################################################
def Start():
    # Set the default ObjectContainer attributes
    ObjectContainer.title1 = TITLE
    ObjectContainer.art    = ART
    
    DirectoryObject.thumb = ICON

    # Set the default cache time
    HTTP.CacheTime             = CACHE_1HOUR
    HTTP.Headers['User-agent'] = HTTP_USER_AGENT

####################################################################################################
@handler(PREFIX, TITLE, art = ART, thumb = ICON)
def MainMenu():
    oc = ObjectContainer()
    
    element = HTML.ElementFromURL(BASE_URL + '/videoklipp/')
    
    for item in element.xpath("//*[contains(@class,'videos-grid-module')]"):
        id = item.xpath("./@id")[0]
        title = unicode(item.xpath(".//header/h2/text()")[0].strip())
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Videos,
                        id = id,
                        title = title
                    ),
                title = title
            )
        )
        
    oc.add(
        DirectoryObject(
            key = Callback(Live),
            title = 'Live'
        )
    )
    
    return oc

####################################################################################################
@route(PREFIX + '/Live')
def Live():
    oc = ObjectContainer(title2 = 'Live')
    
    element = HTML.ElementFromURL(BASE_URL + '/live/')
    
    for item in element.xpath("//*[contains(@class,'live-item-container')]//a"):
        url = item.xpath("./@href")[0]
        title = unicode(item.xpath(".//h4/text()")[0].strip())
        
        time_info = item.xpath(".//time/text()")[0].strip()
        time_info = time_info + " " + item.xpath(".//time/span/text()")[0].strip()
        summary = time_info + '\r\n\r\n' + unicode(item.xpath(".//*[@class='label']/text()")[0].strip())
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Video,
                        url = url,
                        title = title,
                        time_info = time_info
                    ),
                title = title,
                summary = summary
            )
        )
        
    return oc

####################################################################################################
@route(PREFIX + '/Videos')
def Videos(id, title):
    oc = ObjectContainer(title2 = unicode(title))
    
    element = HTML.ElementFromURL(BASE_URL + '/videoklipp/')
    
    for item in element.xpath("//*[@id='" + id + "']//*[contains(@class,'num-')]"):
        url = item.xpath("./@href")[0]
        title = unicode(item.xpath(".//*[@class='label']/text()")[0].strip())
        summary = unicode(item.xpath(".//h4/text()")[0].strip())
        thumb = item.xpath(".//img/@src")[0]
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Video,
                        url = url,
                        title = title
                    ),
                title = title,
                summary = summary,
                thumb = thumb
            )
        )
    
    return oc

####################################################################################################
@route(PREFIX + '/Video')
def Video(url, title, time_info=''):
    oc = ObjectContainer(title2 = unicode(title))
    
    element = HTML.ElementFromURL(url)
    
    playerKey = element.xpath("//param[@name='playerKey']/@value")[0]
    videoPlayer = element.xpath("//param[@name='@videoPlayer']/@value")[0]

    video_url = 'http://c.brightcove.com/services/viewer/htmlFederated?playerKey=%s&dynamicStreaming=true&%%40videoPlayer=%s&refURL=http://www.viasatsport.se/videoklipp/' % (playerKey, videoPlayer)

    try:
        mdo = URLService.MetadataObjectForURL(video_url)
        mo = URLService.MediaObjectsForURL(video_url)
    
        oc.add(
            VideoClipObject(
                url = video_url,
                title = mdo.title,
                summary = mdo.summary,
                thumb = mdo.thumb,
                originally_available_at = mdo.originally_available_at,
                duration = mdo.duration
            )
        )
    except:
        if '/live/' in url:
            oc.header = unicode("Sändningen har ej påbörjats")
            oc.message = unicode("Sändningen startar " + time_info)
        else:
            oc.header = unicode("Kunde ej hitta någon video")
            oc.message = unicode("Var god försök igen")
    
    return oc