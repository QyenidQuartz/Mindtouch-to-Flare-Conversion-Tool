import xml.parsers.expat
import http.client
import urllib.request
import os
import sys

global pageURLSet
global pageTitleSet
global baseURL
pageURLSet = False
pageTitleSet = False

def page_parser_start(name, attrs):
	global pageURLSet
	global pageTitleSet
	global contentURL

	if name == 'page':
		contentID = attrs['id']
		contentURL = url + "/" + contentID + "/contents"
		pageURLSet = True
	if name == 'uri.ui':
		pageTitleSet = True


def page_parser_chardata(data):
	global fileName
	global pageURLSet
	global contentURL
	global pageTitleSet
	global baseURL
	global storageLocation

	if pageTitleSet == True and pageURLSet == True:
		folderChunk = data.split(baseURL)[1]
		folderChunk = folderChunk.replace("/", "\\")
		fileName = storageLocation + "\\" + "".join(x for x in folderChunk if x.isalpha() or x.isdigit() or x == "\\" or x == "_" or x == "%" or x == "-" or x == ".") + '.htm'
		if fileName == storageLocation + ".htm":
			fileName = storageLocation + "index.htm"
		print("Accessing " + contentURL)
		try:
			c = urllib.request.urlopen(contentURL)
			contentAccessible = True
		except:
			print("ERROR: Unable to access: " + contentURL)
			contentAccessible = False
		if contentAccessible:
			try:
				if not os.path.isdir(storageLocation + "\\" + folderChunk):
					print('Creating new folder: ' + storageLocation + "\\" + folderChunk)
					os.makedirs(storageLocation + "\\" + folderChunk)
			except:
				print("ERROR: Unable to create folder path: " + storageLocation + "\\" + folderChunk)
			try:
				f = open(fileName, 'a')
				f.write("<html><head></head><body>")
				f.close()
			except:
				print("ERROR: Unable to write to file: " + fileName)
			ContentsParser = xml.parsers.expat.ParserCreate()
			ContentsParser.StartElementHandler = start_content_element
			ContentsParser.CharacterDataHandler = data_handler_content_element
			ContentsParser.EndElementHandler = end_content_element
			ContentsParser.buffer_text = True
			ContentsParser.Parse(c.read())
		pageTitleSet = False
		pageURLset = False

def page_parser_end(name):
	global fileName
	# Close out our file
	if name == 'page':
		try:
			f = open(fileName, 'a')
			f.write("</body></html>")
			f.close()
		except:
			pass

def start_content_element(sub_name, sub_attrs):
	pass
		
def data_handler_content_element(data):
	print("Opening Local File " + fileName)
	try: 
		f = open(fileName, 'a')
		print("Writing to File")
		f.write(data)
		f.close()
		print("Saved " + fileName)
	except:
		pass

def end_content_element(name):
	pass

print('MindTouch to HTM Conversion Script\nWritten by Ryan Cerniglia\nLast Updated 2011-11-28')
#baseURL = input('URL: ')
baseURL = 'http://wiki.us.sios.com/'
url = baseURL
# Add the suffix for the main pages listing
url += '@api/deki/pages'
		
print("Connecting to " + url)
u = urllib.request.urlopen(url)

global storageLocation
storageLocation = 'C:\\' + baseURL.split('http://')[1]

if not os.path.isdir(storageLocation):
	print('Creating folder: ' + storageLocation)
	os.makedirs(storageLocation)


XMLparser = xml.parsers.expat.ParserCreate()
XMLparser.StartElementHandler = page_parser_start
XMLparser.CharacterDataHandler = page_parser_chardata
XMLparser.EndElementHandler = page_parser_end
print("Downloading file list from " + url)
XMLparser.Parse(u.read(), True)

# Clip links
# Copy images locally