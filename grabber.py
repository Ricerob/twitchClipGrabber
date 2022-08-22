import sys
import os
import argparse
from datetime import date
from moviepy.editor import *

from requests_html import HTMLSession


def render_page(url, user):
    print("Starting HTML Session...")
    session = HTMLSession()
    r = session.get(url)
    print("Rendering Page in Background...")
    r.html.render(sleep=3, keep_page=True, scrolldown=2)

    # We can use .find with a containing attribute to do filtering while gathering - later implementation
    print("Grabbing videos...")

    # Attempt to find views
    articles = r.html.find('article')
    articles_links = []
    for article in articles:
        articles_links.append("https://twitch.tv" + str(article.find('a')[0].attrs['href'].split('?')[0]))

    # Close Session
    session.close()

    return articles_links


def get_mp4_link(url):

    # Session set-up
    session = HTMLSession()
    r = session.get(url)
    r.html.render(sleep=1, scrolldown=1)

    # Grab video title - defaults to last 16 of url if not found for whatever reason
    try:
        video_title = r.html.find('h2', first=True).text
        print("\nClip title: " + video_title)
    except AttributeError:
        print("Clip title not found - default is url")
        video_title = url[-16:]

    session.close()

    # Attempt to grab download link
    try:
        download_link = r.html.find('video', first=True).attrs['src']
    except IndexError:
        # r.html.find fails to find the video tag for some reason
        download_link = ''

    video_info = {'name': video_title, 'dl_link': download_link}
    return video_info


def download_clips(recent_clips, args):
    if not os.path.exists('./temp/' + str(args.user)):
        os.makedirs('./temp/' + str(args.user))

    # List of failed video grabs with links so users can download manually
    failed = {}

    today = date.today()
    videofileclips = []

    for idx, url in enumerate(recent_clips, start=1):
        dl_info = get_mp4_link(url)
        if dl_info['dl_link'] == '':
            print("Clip " + str(idx) + " failed to grab video link, skipping.")
            failed[dl_info['name']] = url
            continue
        print("Downloading clip " + str(idx) + "...")

        r = HTMLSession().get(dl_info['dl_link'])

        # Scrub link for proper filename usage
        dl_info['name'] = "".join(x for x in dl_info['name'] if x.isalnum() or x == ' ')

        # Download video file
        with open('temp/' + str(args.user) + '/' + dl_info['name'] + '.mp4', 'wb') as file:
            file.write(r.content)

        # If a compilation, add to list for later concatenation
        if args.comp is True:
            clip = VideoFileClip('temp/' + str(args.user) + '/' + dl_info['name'] + '.mp4')
            videofileclips.append(clip)

        print("Downloaded clip " + str(idx) + " to ./temp/" + str(args.user) + ".")

    # If a compilation, create compilation and download
    if args.comp is True:
        compilation = concatenate_videoclips(videofileclips)
        compilation.write_videofile('temp/' + str(args.user) + '/' + str(today.strftime('%B%d')) + ' comp.mp4')
    print("\n! Download Finished !")
    return failed


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
    parser.add_argument('-cm', '--compilation', dest='comp', required=False, action='store_true')

    # Grab arguments
    args = parser.parse_args()
    user = args.user
    timeframe = args.timeframe
    limit = args.limit
    compilation = args.comp

    # Grab recent clips and put into sorted dict by views
    link = "https://www.twitch.tv/" + user + "/clips?filter=clips&range=" + timeframe
    recent_clips = render_page(link, user)

    # ... User has no recent clips in this timeframe
    if len(recent_clips) == 0:
        print("User doesn't have any recent clips.")
        sys.exit(0)

    # Download clips
    print("Attempting to download " + str(min(len(recent_clips), limit)) + " clips")
    if limit == 0:
        failed = download_clips(recent_clips, args)
    else:
        failed = download_clips(recent_clips[:limit], args)

    # Print failed clips
    if len(failed) > 0:
        print("\nHere are clips that failed to download: ")
        for name, url in failed.items():
            print(name, ", link: " + url)
