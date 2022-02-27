import sys
import os
import argparse
import time
from requests_html import HTMLSession


def render_page(url, user):
    print("Starting HTML Session...")
    session = HTMLSession()
    r = session.get(url)
    print("Rendering Page in Background...")
    r.html.render(sleep=2, keep_page=True, scrolldown=1)

    # We can use .find with a containing attribute to do filtering while gathering - later implementation
    print("Grabbing videos...")
    videos = r.html.absolute_links

    # Close Session
    session.close()

    # Scrub video links
    print("Filtering Videos...")
    filter_keyword = "https://www.twitch.tv/" + user + "/clip/"
    filtered_list = [n for n in videos if filter_keyword in n]
    scrubbed_urls = []
    for url in filtered_list:
        scrubbed_urls.append(url.split('?')[0])
    return scrubbed_urls


def get_mp4_link(url):

    # Session set-up
    session = HTMLSession()
    r = session.get(url)
    r.html.render(sleep=1, scrolldown=1)

    # Grab video title - defaults to last 16 of url if not found for whatever reason
    print("Video URL: " + url)
    try:
        video_title = r.html.find('h2', first=True).text
        print("Clip title: " + video_title)
    except AttributeError:
        print("Clip title not found - default is url")
        video_title = url[:-16]

    # Grab video link - sometimes nonfunctional
    video_link = r.html.find('video', first=True).attrs['src'].split('?')[0]
    print(str(r.html.find('video', first=True).attrs))
    print("Video link: " + str(video_link))
    video_link_split = video_link.split('/')

    session.close()

    # Attempt to grab download link
    print("Video link split: " + str(video_link_split))
    try:
        download_link = 'https://clips-media-assets2.twitch.tv/' + str(video_link_split[3])
        print("Download link: " + download_link)
    except IndexError:
        print("Parsing Download link failed - failed to grab video tag")
        print("Expected list of length 3, got: " + str(video_link_split))
        download_link = ''

    video_info = {'name': video_title, 'dl_link': download_link}
    return video_info

def download_clips(recent_clips, args):
    if not os.path.exists('./temp/' + str(args.user)):
        os.makedirs('./temp/' + str(args.user))

    for idx, url in enumerate(recent_clips):
        dl_info = get_mp4_link(url)
        if dl_info['dl_link'] == '':
            print("Clip " + str(idx) + " failed to grab video link, skipping.")
            continue
        print("Downloading clip " + str(idx) + "...")

        r = HTMLSession().get(dl_info['dl_link'])

        # Scrub link for proper filename usage
        dl_info['name'] = "".join(x for x in dl_info['name'] if x.isalnum())

        with open('temp/' + str(args.user) + '/' + dl_info['name'] + '.mp4', 'wb') as file:
            file.write(r.content)
        print("Downloaded clip " + str(idx) + " to ./temp/" + str(args.user) + ".")
    print("Download Finished")
    session.close()


if __name__ == '__main__':
    # Argument Parsing
    parser = argparse.ArgumentParser(description="Clip Grabbing Details")
    parser.add_argument('-u', '--user', dest='user', metavar='', required=True, type=str,
                        help='Name of streamer to grab clips from')
    parser.add_argument('-t', '--timeframe', dest='timeframe', metavar='', required=False, type=str,
                        default='7d', choices=['24hr', '7d', '30d', 'all'],
                        help='Timeframe for grabbing clips - default is a week')
    parser.add_argument('-l', '--limit', dest='limit', metavar='', required=False, type=int,
                        default=0, help='Limit on how many clips to download at once')

    args = parser.parse_args()
    user = args.user
    timeframe = args.timeframe
    limit = args.limit


    # Grab recent clips
    link = "https://www.twitch.tv/" + user + "/clips?filter=clips&range=" + timeframe
    recent_clips = render_page(link, user)
    if len(recent_clips) == 0:
        print("User doesn't have any recent clips.")
        sys.exit(0)
    # print("Here are " + user + "'s top clips from the past " + timeframe + ":")
    # print(recent_clips)

    # Download clips
    if limit == 0:
        download_clips(recent_clips, args)
    else:
        print(recent_clips[:limit])
        download_clips(recent_clips[:limit], args)
