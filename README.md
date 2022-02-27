# Twitch Clip Grabber 🖥
Python script to grab and download top clips for a given streamer.

## Use 💾
This script currently supports clip limits on download and 
  `py main.py -u [streamer username] -t [timeframe: '24hr', '7d', '30d', 'all'] -l [clip limit]`
  
## Dependencies 📦
It's recommended to use Python 3.9+. This script relies on the [Requests-HTML](https://docs.python-requests.org/projects/requests-html/en/latest/) Python library v0.3.4.

### Planned Features and Updates 🚀
- Compilation mode
  - Single streamer compilations
  - Multi streamer compilations
- Support for catagories, not just streamers
- Better documentation
- More argument handling
- Quality selection

### Notes
- This script requires a stable and, albeit, fast internet connection. Until it's updated with Async/Await HTMLConnections, if your internet isn't fast enough, it may timeout establishing a connection.
- Clips are downloaded in the highest quality available, for now. This means downloading a ton of clips at the highest quality may take up a considerable amoutn of space - please utilize the limit parameter.
- This script is slow. Feel free to contribute any time-saving mechanisms or ideas - I'm new to this library (and Python)!
