import argparse
import urllib2
import os
import sys
import time
from lxml import etree
import lxml.html 
import StringIO

# command line option parsing
argument_parser = argparse.ArgumentParser(description='Convert a Mindtouch wiki to a Flare project')
argument_parser.add_argument('-i', '--interactive', help='force interactive mode', action='store_true')
argument_parser.add_argument('-u', '--url', help='url of a mindtouch wiki system')
argument_parser.add_argument('-o', '--output', help='local directory to store the new help system (default: current directory)')
argument_parser.add_argument('-a', '--username', help='username for http authentication')
argument_parser.add_argument('-p', '--password', help='password for http authentication')
argument_parser.add_argument('-v', '--verbose', help='turn on verbose console output', action='store_true')

# interactive mode handling
def interactive_mode():
    try:
        url = get_url()
        directory = get_directory()
        if raw_input("Do you have a Mindtouch wiki username / password? ") in {"yes", "y", "Yes", "Y"}:
            username = get_username()
            password = get_password()
    except:
        raise
    return [url, directory]

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

def get_username():
    print "Please provide a Mindtouch wiki username"
    username = raw_input("Username: ")
    return username

def get_password():
    print "Please provide a Mindtouch wiki password"
    password = raw_input("Password: ")
    return password

# Make sure we can connect to the given url
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
    finally:
        f.close()
        
    # Check to see if the Mindtouch API is available
    mindtouch_api_url = url + "@api/deki"
    try:
        print "Accessing " + mindtouch_api_url
        f = urllib2.urlopen(mindtouch_api_url)
        print "Successfully accessed " + mindtouch_api_url
    except urllib2.URLError, e:
        print e
    except urllib2.HTTPError, e:
        print e
    except:
        print "Unknown error accessing " + mindtouch_api_url
    finally:
        f.close()
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
            except:
                print "Unknown error occurred when trying to create " + directory
            else:
                return directory
        else:
            raise StandardError

def link_path_generator(link_url, page_url):
    # Split these by forward slashes
    page_url_split = page_url.split('/')
    link_url_split = link_url.split('/')
    segments_to_check = None
    equal_segements = None
    link_path = ""

    # only go through the lesser length
    if len(page_url_split) > len(link_url_split):
        segments_to_check = len(page_url_split)
    else:
        segments_to_check = len(link_url_split)
    
    # Check the first segment; if they are not equal it's an external link and we can return it
    if page_url_split[0] != link_url_split[0]:
        return link_url    

    # Loop through until we see a difference
    for i in range(segments_to_check):
        if page_url_split[i] != link_url_split[i]:
            equal_segments = i
            break
    else:
        equal_segments = len(link_url_split)

    # Remove the common chunks from the path
    for i in range(equal_segments):
        page_url_split.pop(0)
        link_url_split.pop(0)
    
    # If we still have chunks in the page url, then we need to prepend "../" to the link path
    for i in range(len(page_url_split)):
        link_path = "../" + link_path

    # Everything remaining in the link URL is unique and therefore needs to be in the link path
    for i in range(len(link_url_split) - 1):
        link_path = link_path + link_url_split[i] + '/'
    
    # If we don't have an extension, assume it's a page link
    # We're checking for an extension by counting how many digits from the right our last period was
    if len(link_path.rsplit('.', 1)) <=4:
        link_path = link_path + ".htm"
    
    return link_path

# Program entry point

args = argument_parser.parse_args()
url = args.url
directory = args.output 
username = args.username
password = args.password
verbose = args.verbose
print "Mindtouch Wiki to Flare Project Conversion Tool"
if args.interactive == True:
    try:
        results = interactive_mode()
    except:
        print "Error occured, help system was not converted."
        sys.exit(1)
    else:
        url = results[0]
        directory = results[1]
        if results.length > 2:
            username = results[2]
            password = results[3]
else:
    try:
        url = verify_url(url)
        directory = verify_directory(directory)
    except:
        print "Error occured, help system was not converted."
        sys.exit(1)

# Make our url handler use our username and password
if username or password:
    print "Using " + username + " with a password"
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, username, password)
    handler = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(handler)
    opener.open(url)
    urllib2.install_opener(opener)

print "Beginning content download"

# Go through the page listing, and start grabbing from each page
try:
    page_listing_url = url + "@api/deki/pages"
    page_listing_urlopen = urllib2.urlopen(page_listing_url)
    page_listing = page_listing_urlopen.read()
    page_listing_urlopen.close()
except Exception, e:
    print "Error when accessing Mindtouch wiki page list at " + page_listing_url
    print e

page_url = None
page_title = None
page_path = None
page_contents = None
for event, element in etree.iterparse(StringIO.StringIO(page_listing), events=("start", "end"), huge_tree=True):
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
            page_path = element.text
            # A double-forward slash "//" is an escaped single slash; we need to convert those first
            page_path = page_path.replace("//", "%2F%2F")
            # If we can't find a slash, we're in the root directory
            if page_path.find('/') == -1:
                page_path = ""
            else:
                # We don't want the last bit after the slash as that's the file name
                page_path = page_path.rsplit('/', 1)[0] + "/"
        except:
            # If we've excepted, then we're not dealing with a text string for the path
            # This is usually a self-closing tag in the XML, indicative of a root topic 
            page_path = ""
        # Make page-path
    if element.tag == "page" and event == "end":
        element.clear()
    
    if page_url != None and page_title != None and page_path != None:
        file_path = directory + url.split('http://')[1] + page_path
        full_file_path = file_path + page_title.replace("/", " ") + ".htm"
        print "Creating topic file " + full_file_path.encode('utf-8')
        try:
            os.makedirs(file_path.encode('utf-8'))
            if verbose:
                print "Created directory " + file_path.encode('utf-8')
        except:
            if verbose:
                print "Directory " + file_path.encode('utf-8') + " already exists"
        try:
            # Create a new topic and open it for writing 
            f = open(full_file_path.encode('utf-8'), 'w')
        except:
            print "Error creating file " + full_file_path.encode('utf-8')
        if verbose:
            print "Accessing " + page_url.encode('utf-8')
        try:
            # Access the page URL
            page_content_listing = urllib2.urlopen(page_url.encode('utf-8'))
            try:
                for inner_event, inner_element in etree.iterparse(page_content_listing):
                    # Get the contents of the body tag, unless it has the "toc" attribute
                    if not inner_element.attrib:
                        if inner_element.tag == "body":
                            if verbose:
                                print "Parsing HTML contents"
                            # parse through the html contents
                            page_contents_tree = lxml.html.fragment_fromstring(inner_element.text, create_parent=True)
                            context = etree.iterwalk(page_contents_tree)
                            for action, elem in context:
                                if elem.tag == "a" and "href" in elem.attrib:
                                    # fix links
                                    if verbose:
                                        print "Patching link to " + elem.attrib["href"]
                                    elem.attrib["href"] = link_path_generator(elem.attrib["href"], page_url)
                                if elem.tag == "img" and "src" in elem.attrib:
                                    full_image_path = None
                                    image_url = elem.attrib["src"].split('?')[0]
                                    if image_url.find(url) != -1:
                                        image_path = image_url.split(url)[1].rsplit('/', 1)[0] + "/"
                                        image_file_path = directory + url.split('http://')[1] + image_path
                                        image_file_name = image_url.split(url)[1].rsplit('/', 1)[1]
                                        if verbose:
                                            print "Downloading image file " + image_url
                                        try:
                                            image_urlobject = urllib2.urlopen(image_url)
                                            image_object = image_urlobject.read()
                                            image_urlobject.close()
                                        except urllib2.URLError, e:
                                            print "Error downloading image file " + image_url
                                            
                                        except:
                                            print "Error downloading image file " + image_url
                                        try:
                                            os.makedirs(image_file_path.encode('utf-8'))
                                        except:
                                            if verbose:
                                                print "Path " + image_file_path.encode('utf-8') + " already exists"
                                        else:
                                            if verbose:
                                                print "Created path " + image_file_path.encode('utf-8')
                                        try:
                                            full_image_path = image_file_path + image_file_name
                                            if verbose:
                                                print "Writing image file " + full_image_path.encode('utf-8')
                                            image_file = open(full_image_path.encode('utf-8'), 'wb')
                                            image_file.write(image_object)
                                            image_file.close()
                                        except:
                                            print "Error writing local file " + full_image_path
                                        if verbose:
                                            print "Patching image link in " + full_file_path
                                        elem.attrib["src"] = link_path_generator(elem.attrib["src"], page_url)
                                    
            except:
                print "Error parsing contents of " + page_url.encode('utf-8')
            page_contents = lxml.html.tostring(page_contents_tree)
            page_content_listing.close()
        except:
            print "Error accessing " + page_url.encode('utf-8')
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
        finally:
            f.close()
        print "Finished writing file " + full_file_path.encode('utf-8')
        print " "
        page_url = None
        page_title = None
        page_path = None
        file_path = None
        # Sleep so we do not over-saturate the server
        time.sleep(3)
