import argparse
import urllib2
import os
from lxml import etree

# command line option parsing
argument_parser = argparse.ArgumentParser(description='Convert a Mindtouch wiki to a Flare project')
argument_parser.add_argument('-i', dest='interactive_mode', help='force interactive mode', action='store_true')
argument_parser.add_argument('-u', '--url', help='url of a mindtouch wiki system')
argument_parser.add_argument('-o', '--output', help='local directory to store the new help system (default: current directory)')

# interactive mode handling
def interactive_mode():
    try:
        url = get_url()
        directory = get_directory()
    except:
        raise
    return [url, directory]

# interactive url handler
def get_url():
    url_is_ok = False
    while not url_is_ok:
        print "Please provide the front-page URL of the help system (example: http://www.example.com/wiki/):"
        url = raw_input("URL: ")
        try:
           url = verify_url(url)
           url_is_ok = True
        except:
            if raw_input("Error while verifying url, continue? ") in {"no", "n", "No", "N"}:
                raise
        else:
            return url

# interactive directory handler
def get_directory():
    directory_is_ok = False
    while not directory_is_ok:
        print "Please provide the local directory where you want to save the Flare project to (leave blank for current directory):"
        directory = raw_input("Directory: ")
        try:
           directory = verify_directory(directory)
        except:
            if raw_input("Error while verifying directory, continue? ") in {"no", "n", "No", "N"}:
                raise
        else:
            return directory

# make sure we can connect to the given url
def verify_url(url):
    # make sure we have some text
    if url == "":
        return False
    # Make sure our URL is in the correct format 
    # Should start with http
    if url.split("://")[0] != "http":
        print "Adding 'http://' to the beginning of the url"
        url = "http://" + url
    # Should have ending slash
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
    mindtouch_api_url = url + "@api/deki"
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

# Make sure we can place folders and files in the given directory
def verify_directory(directory):
    # if we wern't given a directory, use the current directory
    if directory == "":
        directory = os.getcwd()
    # attempt to access the directory for writing
    if os.access(directory, os.W_OK):
        print "Able to access " + directory
        return directory
    else:
        print "Unable to access " + directory
        # Ask if we should create the given directory
        if raw_input("Try to create " + directory + "? ") in {"Yes", "yes", "Y", "y"}:
            try:
                # make sure we can access the new directory
                os.makedirs(directory)
                os.access(directory, os.W_OK)
            except os.error, e:
                print e
                raise
            except:
                print "Unknown error occurred when trying to create " + directory
                raise
            else:
                return directory
        else:
            raise StandardError
        
# Program entry point
args = argument_parser.parse_args()
print "Mindtouch Wiki to Flare Project Conversion Tool"
url = args.url
directory = args.output 
if args.interactive_mode == True:
    try:
        results = interactive_mode()
    except:
        print "Error occured, help system was not converted."
        sys.exit(1)
    else:
        url = results[0]
        directory = results[1]
else:
    try:
        url = verify_url(url)
        directory = verify_directory(directory)
    except:
        print "Error occured, help system was not converted."
        sys.exit(1)


print "Beginning content download"

# Go through the page listing, and start grabbing from each page
try:
    page_listing_url = url + "@api/deki/pages"
    page_listing = urllib2.urlopen(page_listing_url)
except Exception, e:
    print "Error when accessing Mindtouch wiki page list"
    print e

try:
    page_url = None
    page_title = None
    page_path = None
    page_contents = None
    for event, element in etree.iterparse(page_listing, events=("start", "end")):
        if element.tag == "page" and event == "start":
            if "href" in element.attrib:
                page_title = None
                page_path = None
                page_url = unicode(element.attrib["href"], "ascii") 
                page_url = page_url.split('?redirects')[0] + "/contents"
        if element.tag == "title" and event == "end":
            page_title = element.text
        if element.tag == "path" and event == "end":
	        try:
                if element.text.find('/') == -1:
                    page_path = ""
                else:
                    page_path = element.text.rsplit('/', 1)[0] + "/"
            except:
                # If we've excepted, then we're not dealing with a text string for the path
                # This is usually a self-closing tag in the XML, indicative of a root topic 
                page_path = ""
        if page_url != None and page_title != None and page_path != None:
            file_path = directory + url.split('http://')[1] + page_path
            full_file_path = file_path + page_title
            print "Creating topic file " + full_file_path.encode('utf-8')
            try:
                os.makedirs(file_path.encode('utf-8'))
                print "Created directory " + file_path.encode('utf-8')
            except:
                print "Directory " + file_path.encode('utf-8') + " already exists"
            try:
                # Create a new topic and open it for writing 
                f = open(full_file_path.encode('utf-8'), 'w')
            except:
                print "Error creating " + full_file_path.encode('utf-8')
                raise
            print "Accessing " + page_url.encode('utf-8')
            try:
                # Access the page URL
                for inner_event, inner_element in itree.iterparse(page_url):
                    
                
            except:
                print "Error accessing " + page_url.encode('utf-8')
                raise
            try:
                # Write the starting html content to the topic
                f.write("<html><head><title>" + page_title.encode('utf-8') + "</title></head><body>")
                # Insert an h1 element with the page title
                f.write("<h1>" + page_title.encode('utf-8') + "</h1>")
                # Insert the page contents
                f.write(page_contents.encode('utf-8'))
                # Write the closing tags
                f.write("</body></html>")
            except:
                print "Error writing page contents to file"
                raise
            print " "
            page_url = None
            page_title = None
            page_path = None
            file_path = None
except Exception, e:
    print "Error when parsing page list"
    print e

# Copy the contents
# Fix the links
# Copy the images locally
