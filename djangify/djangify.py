#!/usr/bin/env python

import os
import re
import argparse
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

TEXT = ""

def displayPathInfo():
	dirpath = os.getcwd()
	logging.info("Current Directory is : " + dirpath )
	foldername = os.path.basename(dirpath)
	logging.info( "Directory name is : " + foldername )

def checkLine(line):
	words = ['src', 'href', 'url']
	out = list()
	for word in words:
		if line.__contains__(word):
			out.append((True, word))
	if len(out) == 0:
		return None
	else:
		return out

def containsURL(line):
	URL = "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
	if re.match(URL, line):
		return True
	else:
		return False

def getIndex(line, word):
	index = line.find(word)
	if word in ['url']:
		start = (index + len(word) + 2)
		quote = line[start - 1]
		if quote not in ['\'', '"']:
			start = (index + len(word) + 1)
			quote = line[start - 1]
			if quote == '(':
				end = line.find(')', start)
			else:
				end = line.find(quote, start)
		else:
			end = line.find(quote, start)
	else:
		start = (index + len(word) + 2)
		quote = line[start - 1]
		end = line.find(quote, start)
	return (start, end)

def djangify(line):
	global TEXT
	#print(line)
	if containsURL(line):
		return line
	if line == '#':
		return line
	return " {% static '" + TEXT + line + "' %} "

def processLine(line):
	#line = line.strip()
	instances = checkLine(line)
	#print(line + " " + str(toProcess))
	#print(bcolors.WARNING + line + bcolors.ENDC)

	buffer = line

	if instances:
		for instance in instances:
			index = getIndex(buffer, instance[1])
			out = djangify(buffer[index[0] : index[1]])
			text = buffer[: index[0]] + out + buffer[index[1] :]
			buffer = text
			#if (out != buffer[index[0] : index[1]]):
			#	print(bcolors.WARNING + line + bcolors.ENDC)
			#	print(text)
	
	return buffer

def func(directory, filepath, fname) :

	"""if filepath.__contains__('/'):
		fname = filepath[filepath.rfind('/')+1:]
		extension = filepath[filepath.rfind('.')+1:]
		print(fname + " " + extension)
	else:
		fname = filepath
		extension = filepath[filepath.rfind('.')+1:]
		print(fname + " " + extension)"""
	
	fname = fname.split(".")[0]
	extension = "html"
	save_path = os.path.join(directory,"Modified_files")
	save_path = os.path.join(save_path, fname)
	f= open(save_path + "." + extension , "w+")

	try:
		with open(filepath) as fp:
			line = fp.readline()
			cnt = 1
			while line:
				temp = processLine(line)
				line = fp.readline()
				cnt += 1
				f.write(temp)

	except IOError:
		logging.error('An error occurred trying to read the file.')
	finally:
		f.close()

	logging.info("Succeeded.. Generated Modified_Files/"+ fname  + "."+extension+" in the directory passed.")

def main():
	
	global TEXT

	parser = argparse.ArgumentParser(description='Converts specified html files or all html files to django format within a \n specified directory.')
	parser.add_argument('files', metavar='f', type=str, nargs='*', help='provide file names to convert')
	parser.add_argument('-a', dest='app_name',  type=str, nargs='?', help='provide django app name')
	parser.add_argument('-d', dest='base_directory',  type=str, nargs='?', help='Provide base directory')

	args = parser.parse_args()

	files = args.files
	directory = args.base_directory
	app_name = args.app_name

	if app_name is not None :
		TEXT = app_name+"/"

	if directory is None :
		directory = os.getcwd()

	logging.info("Directory : " + str(directory))
	logging.info("app_name  : " + str(app_name))

	if not os.path.exists(os.path.join(directory,"Modified_files")) :
		os.mkdir(os.path.join(directory,"Modified_files"))

	if files != [] :
		for i in files :
			func(directory, directory+"/"+i,i)
	
	else :
		for file in os.listdir(directory):
			if file.endswith(".html"):
				func(directory, directory+"/"+file,file)