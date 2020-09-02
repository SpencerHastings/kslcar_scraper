# kslcar_scraper
Scrapes data from a KSL search and sorts by location.

## Prerequisites
python3

### python dependencies
- geopy
- bs4
- html5lib
- requests
- jinja2

## Usage
python ksl-scraper.py "{ksl-search-link}"

Example:
python ksl-scraper.py "https://cars.ksl.com/search/make/Subaru;Toyota/priceTo/10000/state/UT/sellerType/Dealership/body/Hatchback/transmission/Automatic/"

Outputs data as a webpage to output.html
