import argparse
import urllib2
import os
from lxml import etree

argument_parser = argparse.ArgumentParser(description='Convert a Mindtouch wiki to a Flare project')
argument_parser.add_argument('-i', dest='interactive_mode', help='force interactive mode', action='store_true')
argument_parser.add_argument('-u', '--url', help='url of a mindtouch wiki system')
argument_parser.add_argument('-o', '--output', help='local directory to store the new help system (default: current directory)')
args = argument_parser.parse_args()

print "Mindtouch Wiki to Flare Project Conversion Tool"

def interactive_mode():
    try:
        url = get_url()
    except:
        print "Could not get URL or directory"
        raise

def get_url():
    print "Please provide the front-page URL of the help system (example: http://www.example.com/wiki/):"
    url = raw_input("URL: ")
    try:
       url = verify_url(url)
    except:
        if raw_input("Error while verifying url, continue? ") in {"no", "n", "No", "N"}:
            raise
        else:
            url = get_url()
    else:
        return url

def get_directory():
    print "Please provide the local directory where you want to save the Flare project to:"
    directory = raw_input("Directory: ")
    try:
       directory = verify_directory(directory)
    except:
        if raw_input("Error while verifying directory, continue? ") in {"no", "n", "No", "N"}:
            raise
        else:
            directory = get_directory()
    finally:
        return directory

def verify_url(url):
    # Make sure we have a url
    if url == "":
        return False
    # Make sure our URL is in the correct format 
    # Should start with http
    if url.split("://")[0] != "http":
        print "Adding 'http://' to the beginning of the url"
        url = "http://" + url
    # Should have ending slas
    if url[len(url)-1] != "/":
        print "Adding '/' to end of URL"
        url = url + "/"

    # See if we can contact the root site
    try:
        print "Accessing " + url
        f = urllib2.urlopen(url)
        print "Successfully accessed " + url
    except urllib2.URLError, e:
        print e
        raise
    except urllib2.HTTPError, e:
        print e
        raise
    except:
        print "Unknown error accessing " + url
        raise
        
    # Check to see if the Mindtouch API is available
    mindtouch_api_url = url + "@api/deki/pages"
    try:
        print "Accessing " + mindtouch_api_url
        urllib2.urlopen(mindtouch_api_url)
        print "Successfully accessed " + url
    except urllib2.URLError, e:
        print e
        raise
    except urllib2.HTTPError, e:
        print e
        raise
    except:
        print "Unknown error accessing " + url
        raise
    return url
def verify_directory(directory):
    if directory == "":
        pass


# Program entry point
url = args.url
directory = args.output 
if args.interactive_mode == True:
    try:
        interactive_mode()
    except:
        print "Error occured, help system was not converted."
else:
    verify_url(url)
    verify_directory(directory)

