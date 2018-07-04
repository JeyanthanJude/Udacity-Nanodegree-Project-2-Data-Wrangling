
# coding: utf-8

# In[ ]:



# In[1]:


import csv
import codecs
import re
import xml.etree.cElementTree as ET
import cerberus
import schema
import pprint



OSM_PATH = "calgary_canada.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
phone_match = re.compile(r'\+1-\d{3}-\d{3}-\d{4}')
POSTCODE = re.compile(r'[A-z]\d[A-z]\s?\d[A-z]\d')
problem_street=re.compile(r'[0-9]')
url_1=re.compile(r'http',re.IGNORECASE)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)



# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

SCHEMA = schema.schema

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","Bay"]

# UPDATE THIS VARIABLE
mapping= { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
           "E": "East",
           "Blvd": "Boulevard",
           "Blvd.": "Boulevard",
           "Cres": "Crescent",
           "Dr": "Drive",
            "N.": "North",
            "N": "North",
            "E.": "East",
            "E": "East",
            "S": "South",
            "S.E": "Southeast",
            "SE": "Southeast",
            "se": "Southeast",
            "South-east": "Southeast",
            "South-west": "Southwest",
            "SW": "Southwest",
            "W.": "West",
            "W": "West",
            "N.E.": "Northeast",
            "n.e.": "Northeat",
            "NE": "Northeast",
            "N.W": "Northwest",
            "N.W.": "Northwest",
            "NW": "Northwest"}


def audit_street_name(street_name,mapping):
    #Checking for match with R.E
    m = street_type_re.search(street_name)
    if m:
        #Extracting Match
        street_type = m.group()
        #Checking in mapping
        if street_type in mapping:
            #Altering the street type
            street_name=street_name[:-len(street_type)]
            street_name=street_name + mapping[street_type]
            #Removing problem streets
        elif problem_street.match(street_type):
            return None
        return street_name
    else:
        return None
    
def phonenumber(phone_number):
    m=phone_match.match(phone_number)
    if m is None:
        #Removing characters other than numbers
        phone_number=re.sub('[^0-9]+', '', phone_number)
        #Checking if the resulting phone number is not more that 11 characters or less than 10
        if len(phone_number) > 11 or len(phone_number)< 10 :
            phone_number=None
        else:
                    
            if phone_number[0]=='1':
                #Formatting if the number starts with '1'
                phone_number='+1-'+ phone_number[1:4] + '-' + phone_number[4:7] + '-' + phone_number[7:]
                return (phone_number)
                    
            else:
                #Formatting if the number starts with any other number
                phone_number='+1-'+ phone_number[0:3] + '-' + phone_number[3:6] + '-' + phone_number[6:]
                return (phone_number)
    return phone_number


def audit_website(url):
    if url_1.match(url)==None:
        if 'www.' in url:
            #Adding http://
            url='https://' + url
            return url
        else:
            #Adding http://www.
            url='https://www.' + url
            return url
    else:
        return url
    
def post_code_edit(post_code):
    m=POSTCODE.match(post_code)
    if m is not None :
        #Checking for spaces
        if " " not in post_code:
            #Fixing the format
            post_code=(post_code[:3] + " " + post_code[3:]).upper()
        return post_code
    #If AB found in the post code
    elif 'AB' in post_code:
        post_code=post_code.strip('AB ')
        return post_code
    #If '-' found in the post code
    elif '-' in post_code:
        post_code=post_code.replace('-',' ')
        return post_code
    else:
        return None

def audit_housenumber(house_number):
    #Checking if the house number is '-1'
    if house_number != '-1':
        if '#' in house_number:
            #Removing '#'
            house_number=house_number.strip('#')
        return house_number
    else:
        return None




def value_tag(element, child, default_tag_type):
    wat = {}
    
    wat['id'] = element.attrib['id']
    if ":" not in child.attrib['k']:
        wat['key'] = child.attrib['k']
        wat['type'] = default_tag_type
    else:
        position = child.attrib['k'].index(":") + 1
        wat['key'] = child.attrib['k'][position:]
        wat['type'] = child.attrib['k'][:position - 1]
    
    if wat['key']=='street':
        a=audit_street_name(child.attrib['v'],mapping)
        if a is not None:
            wat['value']=a
        else:
            return None
       
    
    elif wat['key']=='website':
        b=audit_website(child.attrib['v'])
        if b is not None:
            wat['value']=b
        else:
            return None
       
    
    elif wat['key']=='phone':
        c=phonenumber(child.attrib['v'])
        if c is not None:
            wat['value']=c
        else:
            return None
        
    
    elif wat['key']=='postcode':
        d= post_code_edit(child.attrib['v'])#
        if d is not None:
            wat['value']=d
        else:
            return None
        
    
    elif wat['key']=='housenumber':
        e=audit_housenumber(child.attrib['v'])
        if e is not None:
            wat['value']= e
        else:
            return None
        
    
    else:
        wat['value'] = child.attrib['v']
        
    return wat
    
        
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in node_attr_fields:
                node_attribs[attrib] = element.attrib[attrib]
        
        # For elements within the top element
        for child in element.iter():
            if child.tag == 'tag':
                if problem_chars.match(child.attrib['k']) is not None:
                    continue
                else:
                    new = value_tag(element, child, default_tag_type)
                    if new is not None:
                        tags.append(new)
      
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for attrib,value in element.attrib.iteritems():
            if attrib in way_attr_fields:
                way_attribs[attrib] = value

        pos = 0
        for child in element.iter():
            if child.tag == 'tag':
                if problem_chars.match(child.attrib['k']) is not None:
                    continue
                else:
                    new = value_tag(element, child, default_tag_type)
                    if new is not None:
                        tags.append(new)
            elif child.tag == 'nd':
                new_2 = {}
                new_2['id'] = element.attrib['id']
                new_2['node_id'] = child.attrib['ref']
                new_2['position'] = pos
                pos += 1
                way_nodes.append(new_2)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}



#HELPER FUNCTION
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)



#MAIN FUNCTION
def process_map(file_in, validate):
    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH, validate=True)



