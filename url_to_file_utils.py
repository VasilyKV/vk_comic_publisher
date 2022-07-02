import os
from urllib.parse import urlsplit, unquote

import requests


def download_file(filepath, url):
	directory = os.path.dirname(filepath)
	os.makedirs(directory, exist_ok = True)
	response = requests.get(url)
	response.raise_for_status()
	with open(filepath, 'wb') as file:
		file.write(response.content)


def get_file_extension(url):
	url_parsed = urlsplit (url)
	path_unquoted = unquote(url_parsed.path)
	file_extension = os.path.splitext(path_unquoted)[1]
	return file_extension
	