# simple-web-crawler

Simple web-scraper tool (non-recursive for now) which searches for:
    - Twitter handle
    - Facebook page id
    - iOS App Store id
    - Google Play Store id
        
Written for Python 3.7

- `main.py` contains the startup configuration code.
- `matching.py` is for parsing documents and matching the relevant information.
- `processor.py` contains the driving code directing which files to match and aggregating the results.