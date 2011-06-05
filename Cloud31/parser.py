#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
def detect_links(text):
	items=text.split(" ")
	new_items = []
	for item in items:
		prefix = item[:1]
		link_prefix = item[:7]
		if prefix == "#":
			item_text=re.sub("\W","",item)
			item = '<a href="#'+item_text+'">'+item+'</a>'
			
		if prefix == "@":
			item_text=re.sub("\W","",item)
			item = '<a href="@'+item_text+'">'+item+'</a>'
		
		if link_prefix == "http://":
			item = '<a href="'+item+'">'+item+'</a>'
			
		new_items.append(item)
			
	result = ""
	for item in new_items:
		result += item + " "
	
	return result.strip()

