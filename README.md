# Twitch Clip Grabber
Python script to grab and download top clips for a given streamer.

## Use
This script currently supports clip limits on download and 
  `py main.py -u [streamer username] -t [timeframe: '24hr', '7d', '30d', 'all'] -l [clip limit]`
  
## Dependencies
It's recommended to use Python 3.9+. This script relies on the [Requests-HTML](https://docs.python-requests.org/projects/requests-html/en/latest/) Python library v0.3.4.

### Planned Features and Updates
- Compilation mode
  - Single streamer compilations
  - Multi streamer compilations
- Support for catagories, not just streamers
- Better documentation
- More argument handling
