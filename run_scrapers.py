#!/usr/bin/python

# ./run_scrapers.py text bills votes amendments

import os, os.path, glob, re, hashlib, shutil, sys

CONGRESS = 113
SCRAPER_PATH = "../scripts/congress"

# UTILS

def mkdir(path):
	if not os.path.exists(path):
		os.makedirs(path)

def md5(fn, modulo):
	# do an MD5 on the file but run a regex first
	# to remove content we don't want to check for
	# differences.
	
	data = open(fn).read()
	data = re.sub(modulo, data, "--")
	
	md5 = hashlib.md5()
	md5.update(data)
	return md5.digest()

def copy(fn1, fn2, modulo):
	# Don't copy unchanged files so that we don't touch file modification times.
	if os.path.exists(fn2):
		if md5(fn1, modulo) == md5(fn2, modulo):
			return
	print fn2
	shutil.copyfile(fn1, fn2)

# MAIN

# Set options.

fetch_mode = "--force"
log_level = "error"

if "CACHE" in os.environ:
	fetch_mode = ""
	
# Run scrapers and parsers.

if "people" in sys.argv:
	if CONGRESS != 113: raise ValueErrror()
	
	# Pull latest poeple YAML.
	os.system("cd %s/cache/congress-legislators; git fetch -pq" % SCRAPER_PATH)
	os.system("cd %s/cache/congress-legislators; git merge --ff-only -q origin/master" % SCRAPER_PATH)
	
	# Convert people YAML into the legacy format.
	mkdir("data/us/%d" % CONGRESS)
	os.system("python ../scripts/legacy-conversion/convert_people.py %s/cache/congress-legislators/ data/us/people_legacy.xml data/us/people.xml 0" % SCRAPER_PATH)
	os.system("python ../scripts/legacy-conversion/convert_people.py %s/cache/congress-legislators/ data/us/people_legacy.xml data/us/%d/people.xml 1" % (SCRAPER_PATH, CONGRESS))
	
	# Load YAML (directly) into db.
	os.system("./parse.py person") #  -l ERROR

if "text" in sys.argv:
	# Scrape with legacy scraper.
	# Do this before bills because the process of loading into the db checks for new
	# bill text and generates feed events for text availability.
	mkdir("data/us/bills.text/%d" % CONGRESS)
	os.system("cd ../scripts/gather; perl fetchbilltext.pl FULLTEXT %d" % CONGRESS)
	os.system("cd ../scripts/gather; perl fetchbilltext.pl GENERATE %d" % CONGRESS)
	
if "bills" in sys.argv:
	# Scrape.
	os.system("cd %s; . .env/bin/activate; ./run bills --govtrack %s --congress=%d --log=%s" % (SCRAPER_PATH, fetch_mode, CONGRESS, log_level))

	# Copy files into legacy location.
	mkdir("data/us/%d/bills" % CONGRESS)
	bill_type_map = { 'hr': 'h', 's': 's', 'hres': 'hr', 'sres': 'sr', 'hjres': 'hj', 'sjres': 'sj', 'hconres': 'hc', 'sconres': 'sc' }
	for fn in glob.glob("%s/data/%d/bills/*/*/data.xml" % (SCRAPER_PATH, CONGRESS)):
		congress, bill_type, number = re.match(r".*congress/data/(\d+)/bills/([a-z]+)/(?:[a-z]+)(\d+)/data.xml$", fn).groups()
		if int(congress) != CONGRESS: raise ValueError()
		if bill_type not in bill_type_map: raise ValueError()
		fn2 = "data/us/%d/bills/%s%d.xml" % (CONGRESS, bill_type_map[bill_type], int(number))
		copy(fn, fn2, r'updated="[^"]+"')

	# Load into db.
	os.system("./parse.py --congress=%d bill" % CONGRESS) #  -l ERROR

if "amendments" in sys.argv:
	# Scrape.
	# TODO: GovTrack-style output is not implemented yet.
	os.system("cd %s; . .env/bin/activate; ./run amendments --govtrack %s --congress=%d --log=%s" % (SCRAPER_PATH, fetch_mode, CONGRESS, log_level))

	# Copy files into legacy location.
	mkdir("data/us/%d/bills.amdt" % CONGRESS)
	for fn in glob.glob("%s/data/%d/amendments/*/*/data.xml" % (SCRAPER_PATH, CONGRESS)):
		congress, chamber, number = re.match(r".*congress/data/(\d+)/amendments/([hs])amdt/(?:[hs])amdt(\d+)/data.xml$", fn).groups()
		if int(congress) != CONGRESS: raise ValueError()
		fn2 = "data/us/%d/bills.amdt/%s%d.xml" % (CONGRESS, chamber, int(number))
		print fn, fn2
		#copy(fn, fn2, r'updated="[^"]+"')

if "votes" in sys.argv:
	# Scrape.
	os.system("cd %s; . .env/bin/activate; ./run votes --govtrack %s --congress=%d --log=%s" % (SCRAPER_PATH, fetch_mode, CONGRESS, log_level))
	
	# Copy files into legacy location.
	mkdir("data/us/%d/rolls" % CONGRESS)
	for fn in glob.glob("%s/data/%d/votes/*/*/data.xml" % (SCRAPER_PATH, CONGRESS)):
		congress, session, chamber, number = re.match(r".*congress/data/(\d+)/votes/(\d+)/([hs])(\d+)/data.xml$", fn).groups()
		if int(congress) != CONGRESS: raise ValueError()
		fn2 = "data/us/%d/rolls/%s%s-%d.xml" % (CONGRESS, chamber, session, int(number))
		copy(fn, fn2, r'updated="[^"]+"')
		
	# Load into db.
	os.system("./parse.py --congress=%d vote" % CONGRESS) #  -l ERROR

# TODO: Committee metadata and meetings.
