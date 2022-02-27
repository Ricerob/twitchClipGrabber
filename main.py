import sys
import os
from requests_html import HTMLSession
from bs4 import BeautifulSoup


def render_page(url, user):
    print("Starting HTML Session...")
    session = HTMLSession()
    r = session.get(url)
    print("Rendering Page in Background...")
    r.html.render(sleep=1, keep_page=True, scrolldown=1)

    # We can use .find with a containing attribute to do filtering while gathering - later implementation
    print("Grabbing videos...")
    videos = r.html.absolute_links

    print("Filtering Videos...")
    filter_keyword = "https://www.twitch.tv/" + user + "/clip/"
    filtered_list = [n for n in videos if filter_keyword in n]
    scrubbed_urls = []
    for url in filtered_list:
        scrubbed_urls.append(url.split('?')[0])
    return scrubbed_urls


def get_mp4_link(url):
    session = HTMLSession()
    r = session.get(url)
    r.html.render(sleep=1, keep_page=True, scrolldown=1)
    video_title = r.html.find('h2', first=True).text

    video_link = r.html.find('video', first=True).attrs['src'].split('?')[0]
    video_link_split = video_link.split('/')
    download_link = 'https://clips-media-assets2.twitch.tv/' + video_link_split[3]

    video_info = {'name': video_title, 'dl_link': download_link}
    return video_info

def download_clip(url):
    dl_info = get_mp4_link(url)
    print("Downloading first clip...")

    r = HTMLSession().get(dl_info['dl_link'])

    if not os.path.exists('./temp'):
        os.makedirs('./temp')
    with open('temp/' + dl_info['name']+'.mp4', 'wb') as file:
        file.write(r.content)
    print("Downloaded clip to ./temp/.")


if __name__ == '__main__':
    args = sys.argv[0:]
    if len(args) < 2:
        if args[1] == "-s":
            print("Usage - python3 main.py -s [streamer name]")
        else:  # More commands to come
            print("Too few arguments: python3 main.py -s [streamer name]")
        sys.exit(1)

    user = args[2]
    link = "https://www.twitch.tv/" + user + "/clips?filter=clips&range=7d"
    recent_clips = render_page(link, user)
    if len(recent_clips) == 0:
        print("User doesn't have any recent clips.")
        sys.exit(0)
    #print("Here are " + user + "'s top clips from the past week:")
    #print(recent_clips)
    download_clip(recent_clips[0])

