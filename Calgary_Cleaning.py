
# coding: utf-8

# In[12]:

#!/usr/bin/env python

import xml.etree.cElementTree as ET
from collections import defaultdict
import re

osm_file = open("calgary_canada.osm", "r",encoding="utf8")

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()

        street_types[street_type] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print ("%s: %d" % (k, v)) 

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit():
    for event, elem in ET.iterparse(osm_file):
        if is_street_name(elem):
            audit_street_type(street_types, elem.attrib['v'])    
    print_sorted_dict(street_types)    

if __name__ == '__main__':
    audit()


# In[1]:

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    element_tags={}
    
    for event,element in ET.iterparse(filename):
        x=element.tag
        if x in element_tags:
            element_tags[x] += 1
        else:
            element_tags[x]=1
    return element_tags

def test():

    tags = count_tags('calgary_canada.osm')
    pprint.pprint(tags)
    return tags

print (test())


# In[29]:

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "website")

def audit():
    s=set()
    for event, elem in ET.iterparse('calgary_canada.osm'):
        if is_street_name(elem):
            print (elem.attrib['v'])
    
       


audit()


# In[ ]:

url_1=re.compile(r'http',re.IGNORECASE)
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "website")

def audit():
    
    for event, elem in ET.iterparse('calgary_canada.osm'):
        if is_street_name(elem):
            website=elem.attrib['v']
            if url_1.match(website)== None:
                if 'www.' in website:
                    website= 'https://' + website
                    print(website)
                else:
                    website='https://www.' + website
                    print(website)

audit()


# In[24]:

import re
POSTCODE = re.compile(r'[A-z]\d[A-z]\s?\d[A-z]\d')
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode")

def audit():
    
    for event, elem in ET.iterparse('calgary_canada.osm'):
        if is_street_name(elem):
            x=elem.attrib['v']
            m=POSTCODE.match(x)
            if m is not None :
                if " " not in x:
                    x=(x[:3] + " " + x[3:]).upper()
                    print (x)
            elif 'AB' in x:
                x=x.strip('AB ')
                print ('After STrip:')
                print (x)
            else:
                print ('Defects:')
                print (x)
            
            
audit()                   
                    
            
                
    


# In[18]:

POSTCODE = re.compile(r'[A-z]\d[A-z]\s\d[A-z]\d')
x='T3H3P8'
print (POSTCODE.match(x))


# In[28]:

import re
POSTCODE = re.compile(r'[A-z]\d[A-z]\s?\d[A-z]\d')
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode")

def audit():
    
    for event, elem in ET.iterparse('calgary_canada.osm'):
        if is_street_name(elem):
            post_code=elem.attrib['v']
            m=POSTCODE.match(post_code)
            if m is not None :
                #Checking for spaces
                if " " not in post_code:
                    #Fixing the format
                    post_code=(post_code[:3] + " " + post_code[3:]).upper()
                    
            else:
                #Printing out the rest to analyze
                print ('Defects:')
                print (post_code)
audit()


def post_code_edit(post_code):
    m=POSTCODE.match(post_code)
    if m is not None :
        #Checking for spaces
        if " " not in post_code:
            #Fixing the format
            post_code=(post_code[:3] + " " + post_code[3:]).upper()
            return post_code
    elif 'AB' in post_code:
        post_code=post_code.strip('AB ')
        return post_code
    elif if '-' in post_code:
        post_code=post_code.replace('-',' ')
        return post_code
    else:
        return None
    


# AS visible from the above code a few postal codes are defects. Some of them can be cleaned out but certain ones like the '403-719-6250' ,'1212' etc. are incorrect entries in the field. The '403-719-6250' seems to be a phone number and is an example of column shift where an entry suitable in another field is placed in the wrong field. Postal codes like these can be ignored.

# In[ ]:

#Correcting postal codes with AB
if 'AB' in post_code:
    post_code=post_code.strip('AB ')
if '-' in post_code:
    post_code=post_code.replace('-',' ')
else:
    post_code= None


# In[ ]:




# In[2]:

import xml.etree.cElementTree as ET
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "phone")

def audit():
    s=set()
    for event, elem in ET.iterparse('calgary_canada.osm'):
        if is_street_name(elem):
            print (elem.attrib['v'])
    
       


audit()


# In[3]:

import re
PHONENUM = re.compile(r'\+1-\d{3}-\d{3}-\d{4}')


# In[4]:

s='+1-403-460-3341'
if PHONENUM.match(s):
    print (1)


# In[22]:

import xml.etree.cElementTree as ET
import re
phone_match = re.compile(r'\+1-\d{3}-\d{3}-\d{4}')
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "phone")

def audit():
    for event, elem in ET.iterparse('calgary_canada.osm'):
        if is_street_name(elem):
            phone_number=elem.attrib['v']
            #Looking for match with regular expression
            m=phone_match.match(phone_number)
            if m is None:
                #Removing characters other than numbers
                phone_number=re.sub('[^0-9]+', '', phone_number)
                #Checking if the resulting phone number is not moe that 11 characters
                if len(phone_number) not in range(10,12) :
                    phone_number=None
                else:
                    
                    if phone_number[0]=='1':
                        #Formatting if the number starts with '1'
                        phone_number='+1-'+ phone_number[1:4] + '-' + phone_number[4:7] + '-' + phone_number[7:]
                        print(phone_number)
                    
                    else:
                        #Formatting if the number starts with any other number
                        phone_number='+1-'+ phone_number[0:3] + '-' + phone_number[3:6] + '-' + phone_number[6:]
                        print (phone_number)
audit()


# In[21]:

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:housenumber")

def audit():
    s=set()
    for event, elem in ET.iterparse('calgary_canada.osm'):
        if is_street_name(elem):
            house_number=elem.attrib['v']
            if house_number > 0:
                if '#' in house_number:
                    house_number=house_number.strip('#')
                return house_number
            else:
                return None
    
       
def audit_housenumber(house_number):
    if house_number > 0:
        if '#' in house_number:
            house_number=house_number.strip('#')
        return house_number
    else:
        return None
    

audit()


# In[ ]:



