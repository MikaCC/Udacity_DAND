#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 17:32:18 2017

@author: sicongchen
"""


"""
Count multiple patterns in the tags
reference udacity data wranggling course
"""

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    tag_count = {}
    for _, element in ET.iterparse(filename, events=("start",)):
        add_tag(element.tag, tag_count)
    return tag_count

def add_tag(tag, tag_count):
    if tag in tag_count:
        tag_count[tag] += 1
    else:
        tag_count[tag] = 1
        
OSMFILE = "san-francisco_california.osm"        

pprint.pprint(count_tags(OSMFILE))