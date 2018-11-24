
# coding: utf-8

# In[ ]:


from __future__ import print_function
from googleapiclient.discovery import build
import gspread
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from itertools import islice
import re


# # Key takeaways
# 
# * Use British-English right from the beginning
# * Force the people to be responsible for their stuff
# * Force the people to work on mendeley
# * Force the people to use harvard citation
# * Force the people to write texts with the roughly the same length

# # How does this script work?!
# 
# * The order of the trends is done by the order of the trends_intro and then by the inner order of the groups

# # Configuration
# 
# ## Headlines

# In[1]:


# Abbreviations-Section
ABBREVIATION_TITLE = "List of Abbrevations"
ABBREVIATION_HEADLINE_TAG = "H6"

# Trends-Section
TRENDS_TITLE = "Trends"
TRENDS_DESCRIPTION = ""
TRENDS_SUB_SECTION_HEADLINE_TAG = "H2"
TRENDS_SUB_SECTION_SLOGAN_TAG = "H3"
TRENDS_SUB_SECTION_AREA_HEADLINE_TAG = "H4" # Trend Drivers, Trend Facts ... 
TRENDS_SUB_SECTION_AREA_BULLET_ICON = "•" # List icon for Trend Drivers, Trend Facts ...
TRENDS_SUB_SECTION_AREA_IMPACT_HEADLINE = "Impact on XXX"

# Sources-Section
SOURCES_TITLE = "Sources"
SOURCES_DESCRIPTION = ""
SOURCES_KEY_TAG = "H6"


# # Pipeline
# 
# This pipeline downloads the data from the googel spread sheet and then replaced

# # 1. Help functions

# ## 1.1. Text formatation

# In[17]:


def sanitize_text(text):
    text = text.replace("&", "&amp;")
    return text


# In[18]:


def sanitize_text_test():
    print(sanitize_text("Hello & World") == "Hello &amp; World")

#sanitize_text_test()
    


# In[19]:


def generate_xml_list(text):
    result = "<List>\n"
    li = [s.strip() for s in text.splitlines()]
    for l in li:
        result += "<List-Element>" + TRENDS_SUB_SECTION_AREA_BULLET_ICON + " " + l+ "</List-Element>\n"

    result += "</List>"
    return result


# In[20]:


def generate_xml_list_test():
    print(generate_xml_list("Hello World \n hello / Seb \n hello CDTM\n"))
    
#generate_xml_list_test()


# ## 1.2. Find and replace author

# In[21]:


def find_author_and_replace(text):    
    counter = 0
    authors = dict()
    p = re.compile("\[([a-zäöüÄÖÜA-Z_0-9]*)")
    for match in p.finditer(text):
        key = match.group(1)
        if key not in authors:
            counter += 1
            authors[key] = counter
    
    # print(authors)
            
    for key, value in authors.items():
        text = text.replace("["+key, "["+str(value))
        
    return (text, authors)


# In[22]:


def find_author_and_replace_test():
    test = "The side bar include [KRAUZ, p.22] a Cheatsheet, full [KRAUZ] Reference, sults with the Tools below [SEB], [KAYA]. Replace & List outp [HASE]."
    text, authors = find_author_and_replace(test)
    print(text)
    print(authors)

    
#find_author_and_replace_test()


# ## Download the data from the spreadsheet

# http://www.countingcalculi.com/explanations/google_sheets_and_jupyter_notebooks/

# In[23]:


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '16jza4slLRK4Fe3-O_f410P_-WZBe5EN-fmq_OW3HJNQ'
RANGE_NAME = 'Trends'


# In[24]:


def load_data_from_google_sheets():
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
    gc = gspread.authorize(credentials)
    
    book = gc.open_by_key(SPREADSHEET_ID)
    return book


# In[25]:


book = load_data_from_google_sheets();


# # XML
# 

# ## Abbrevations
# 
# Generate the abbrevations from the sheet and transform it into the XML structure
# 
# ```
# <Abbreviations>
# <Abbreviation><H6>AI</H6>Artificial Intelligence</Abbreviation>
# <Abbreviation><H6>BIM</H6>Building information modeling</Abbreviation>
# <Abbreviation><H6>LCC</H6>Life Cycle Costing</Abbreviation>
# ...
# </Abbreviations>
# ```

# In[26]:


def generate_abbrevations(book):
    worksheet = book.worksheet("Abreviations")
    table = worksheet.get_all_values()
    ##Convert table data into a dataframe
    df = pd.DataFrame(table[1:], columns=table[0])
    # Init XML structure
    result = "<Abbreviations-Section>\n";
    result += "<H1>"+ABBREVIATION_TITLE+"</H1>\n";
    result += "<Abbreviations>\n";
    # Iterate over the rows
    for index, row in islice(df.iterrows(), 1, None):
        # Grab the key and values
        key = sanitize_text(row[0])
        val = sanitize_text(row[1])
        # Create a xml string
        result += "<Abbreviation><"+ABBREVIATION_HEADLINE_TAG+">" + key + "</"+ABBREVIATION_HEADLINE_TAG+">" + val + "</Abbreviation>\n"
    # Add closing tag
    result += "</Abbreviations>\n";
    result += "</Abbreviations-Section>\n";
    return result


# In[27]:


#print(generate_abbrevations(book))


# ## Trends
# 
# Generate the trends from the sheet and transform it into the XML structure
# 
# ```
# <Trends-Section>
# <List>
# <List-Element>Technology Trends</List-Element>
# <List-Element>Societal &amp; Environmental Trends</List-Element>
# </List>
# <Trends-Sub-Sections>
# <Trends-Sub-Section>
# <H1>AI</H1>
# <H3>SUBRTITLE</H3>
# <Text>Intro text for bla bla</Text>
# <Trends>
# <Trend>
# <H2>Trend 1 Title</H2>
# <H3>Slogan</H3>
# <Text>
# Intro text
# <H4>Facts</H4>
# <List>
# <List-Element>Hello World</List-Element>
# <List-Element>Hello CDTM!</List-Element>
# <List-Element>Hello Sebastian</List-Element>
# ...
# </List>
# </Text>
# </Trend>
# </Trends>
# </Trends-Sub-Section>
# ...
# </Trends-Sub-Sections>
# 
# 
# <Abbreviation><H6>BIM</H6>Building information modeling</Abbreviation>
# <Abbreviation><H6>LCC</H6>Life Cycle Costing</Abbreviation>
# ...
# </Abbreviations>
# ```

# In[28]:


def generate_trends(book):
    # Init XML structure
    result = "<Trends-Section>\n";
    result += "<H1>"+TRENDS_TITLE+"</H1>\n";
    # Add description if necessary
    if len(TRENDS_DESCRIPTION) > 0:
        result += "<Text>"+TRENDS_DESCRIPTION+"</Text>\n";
    
    # Init list of trend sections
    result_trend_list = "<List>\n"
    
    # Load trends
    # Trends_intro
    worksheet = book.worksheet("Trend_Intro")
    table = worksheet.get_all_values()
    ##Convert table data into a dataframe
    df_trends_intro = pd.DataFrame(table[1:], columns=table[0])
    # print(df_trends_intro)

    worksheet = book.worksheet("Trends")
    table = worksheet.get_all_values()
    # Convert table data into a dataframe
    df_trends = pd.DataFrame(table[2:], columns=table[0])
    # print(df_trends)
    
    # Start with sub sections
    result_sub_sections = "<Trends-Sub-Sections>\n"
    # Iterate over the trend intro
    for index, row in islice(df_trends_intro.iterrows(), 0, None):
        # Grab the key and values
        key = sanitize_text(row[3])
        intro_text = sanitize_text(row[4])
        intro_responsible = sanitize_text(row[2])
        
        # Init the trend sub section
        result_trend_sub_section = '<Trends-Sub-Section title="'+key+'">\n';
        
        result_trend_sub_section += "<H1>"+ key + "</H1>\n"
        result_trend_sub_section += '<Text responsible="'+intro_responsible+'">'+ intro_text + "</Text>\n"
        
        # Add the trend to the overview list
        result_trend_list += "<List-Element>" + key + "</List-Element>\n"
        
        # Start adding the trends
        result_trend_sub_section += '<Trends>\n'
        
        for trend_index, trend_row in df_trends.loc[df_trends['Sub-Section'] == row[3]].iterrows():
            trend_title = sanitize_text(trend_row[2])
            trend_slogan = sanitize_text(trend_row[7])
            trend_intro = sanitize_text(trend_row[9])
            trend_facts = sanitize_text(trend_row[11])
            trend_drivers = sanitize_text(trend_row[13])
            trend_challanges = sanitize_text(trend_row[15])
            trend_impact = sanitize_text(trend_row[17])
            trend_responsible = sanitize_text(trend_row[5])
            
            result_trend = '<Trend responsible="'+trend_responsible+'">\n'            
            
            result_trend += "<"+TRENDS_SUB_SECTION_HEADLINE_TAG+">" + trend_title + "</"+TRENDS_SUB_SECTION_HEADLINE_TAG+">\n"
            result_trend += "<"+TRENDS_SUB_SECTION_SLOGAN_TAG+">" + trend_slogan + "</"+TRENDS_SUB_SECTION_SLOGAN_TAG+">\n"
            result_trend += "<Text>\n"
            # Trend intro
            result_trend += trend_intro + "\n"
            # Trend Facts
            result_trend += "<"+TRENDS_SUB_SECTION_AREA_HEADLINE_TAG+">"+"Facts:"+"</"+TRENDS_SUB_SECTION_AREA_HEADLINE_TAG+">"+"\n"
            result_trend += generate_xml_list(trend_facts) +"\n"
            # Trend Key Drivers
            result_trend += "<"+TRENDS_SUB_SECTION_AREA_HEADLINE_TAG+">"+"Key Drivers:"+"</"+TRENDS_SUB_SECTION_AREA_HEADLINE_TAG+">"+"\n"
            result_trend += generate_xml_list(trend_drivers) +"\n"
            # Trend Challenges
            result_trend += "<"+TRENDS_SUB_SECTION_AREA_HEADLINE_TAG+">"+"Challenges:"+"</"+TRENDS_SUB_SECTION_AREA_HEADLINE_TAG+">"+"\n"
            result_trend += generate_xml_list(trend_challanges) +"\n"
            # Trend Impact Headline
            result_trend += "<"+TRENDS_SUB_SECTION_AREA_HEADLINE_TAG+">"+TRENDS_SUB_SECTION_AREA_IMPACT_HEADLINE +":"+"</"+TRENDS_SUB_SECTION_AREA_HEADLINE_TAG+">"+"\n"
            result_trend += generate_xml_list(trend_impact) +"\n"
            # Trend Impact Text
            result_trend += "</Text>\n"
            result_trend += "</Trend>\n"
            result_trend_sub_section += result_trend
        
        # Close the trend section
        result_trend_sub_section += '</Trends>\n'
    
        
    
        # Close the trend sub section
        result_trend_sub_section += "</Trends-Sub-Section>\n";

        # Add it to the result
        result_sub_sections += result_trend_sub_section;

    result_sub_sections += "</Trends-Sub-Sections>"
    
    result_trend_list += "</List>"
    
    # Add the elements to the result object
    result += result_trend_list + "\n"
    result += result_sub_sections + "\n"
    result += "</Trends-Section>\n";
    return result  


# ## Sources
# 
# Generate the sources from the sheet and transform it into the XML structure.
# Order the sources by the apperance.
# 
# ```
# <Sources-Section>
# <H1>Source</H1>
# <Sources>
# <Source>
# <H6>1</H6> Sebastians Report 2017 ....
# </Source>
# ...
# </Sources>
# </Sources-Section>
# ```

# In[29]:


def generate_sources(book, map_hash_source):
    # invert the mapping NUMBER -> HASH
    map_number_hash = {v: k for k, v in map_hash_source.items()}
    
    # Init an array with the size of the sources
    sources = [("","")]*len(map_hash_source)
       
    worksheet = book.worksheet("Sources")
    table = worksheet.get_all_values()
    # Convert table data into a dataframe
    df = pd.DataFrame(table[1:], columns=table[0])
    # print(df_trends)
    
    # Start with sub sections
    result = "<Sources-Sections>\n"
    result += "<H1>"+SOURCES_TITLE+"</H1>\n"
    result += "<Text>"+SOURCES_DESCRIPTION+"</Text>\n"
    # Start with the list
    result += "<Sources>\n"
    # Iterate over the sources array
    for index, row in islice(df.iterrows(), 1, None):
        key = sanitize_text(row[0])
        responsible = sanitize_text(row[2])
        val = sanitize_text(row[4])
        if key in map_hash_source:
            # Find the number of the source
            source_index = map_hash_source[key]-1
            # Add the value of the source to the right order of the array
            sources[source_index] = (val, responsible)
        else:
            print("Source not used", responsible , key)
        
    # Iterate of the ordered source array and genrate the xml
    for index, (source, responsible) in enumerate(sources):
        
        if (len(source) == 0):            
            print("Source not declared", map_number_hash[index+1])
        else:
            result += '<Source responsible="'+responsible+'">\n'
            result += "<" + SOURCES_KEY_TAG + ">" + str(index+1) + "</" + SOURCES_KEY_TAG + "> "
            result += source
            result += "\n"
            result += "</Source>\n"
    
    # Close the xml tags
    result += "</Sources>\n"    
    result += "</Sources-Sections>\n"
    
    return result


# In[30]:


def run():
    book = load_data_from_google_sheets()
    xml = ""
    # Add Abbreviations
    xml += generate_abbrevations(book)
    # Add Trends
    xml += generate_trends(book)
    # Add Scenarios
    # Add Ideation
    # Add Sources    


    # Replace the citation
    xml, authors = find_author_and_replace(xml)
    xml += generate_sources(book, authors)
    # Wrap the root object arround all
    xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Root>\n' + xml + '</Root>'
    #print(xml)
    return xml


# In[31]:


#run()

