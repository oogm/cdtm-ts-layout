
# coding: utf-8

# In[43]:


from __future__ import print_function
from googleapiclient.discovery import build
import gspread
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from itertools import islice
import re
from lxml import etree


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

# In[44]:


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

# In[45]:


def sanitize_text(text):
    text = text.replace("&", "&amp;")
    return text


# In[46]:


def sanitize_text_test():
    print(sanitize_text("Hello & World") == "Hello &amp; World")

#sanitize_text_test()
    


# In[47]:


def generate_xml_list(text):
    result = "<List>\n"
    li = [s.strip() for s in text.splitlines()]
    for l in li:
        result += "<List-Element>" + TRENDS_SUB_SECTION_AREA_BULLET_ICON + " " + l+ "</List-Element>\n"

    result += "</List>"
    return result


# In[48]:


def generate_xml_list_test():
    print(generate_xml_list("Hello World \n hello / Seb \n hello CDTM\n"))
    
#generate_xml_list_test()


# ## 1.2. Find and replace author

# In[49]:


def find_author_and_replace(text):    
    counter = 0
    authors = dict()
    p = re.compile("\[([a-zäöüÄÖÜA-Z_0-9]*)")
    for match in p.finditer(text):
        key = match.group(1)
        if key not in authors and len(key) > 0:
            counter += 1
            authors[key] = counter
    
    # print(authors)
            
    for key, value in authors.items():
        text = text.replace("["+str(key), "["+str(value))
        
    return (text, authors)


# In[50]:


def find_author_and_replace_test():
    test = "The side bar include [] [KRAUZ, p.22] a Cheatsheet, full [KRAUZ] Reference, sults with the Tools below [SEB], [KAYA]. Replace & List outp [HASE]. [KRAUZ] [KRAUZ] [KRAUZ] [KRAUZ]"
    text, authors = find_author_and_replace(test)
    #print(text)
    #print(authors)

    
find_author_and_replace_test()


# ## Download the data from the spreadsheet

# http://www.countingcalculi.com/explanations/google_sheets_and_jupyter_notebooks/

# In[51]:


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '16jza4slLRK4Fe3-O_f410P_-WZBe5EN-fmq_OW3HJNQ'
RANGE_NAME = 'Trends'


# In[52]:


def load_data_from_google_sheets():
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
    # print(credentials)
    gc = gspread.authorize(credentials)
    
    book = gc.open_by_key(SPREADSHEET_ID)
    return book


# In[53]:


book = load_data_from_google_sheets();
# print(book)


# # XML

# ## Scenarios
# 
# Generate scenario XML from excel sheet
# ```
# <Scenarios>
#   <Scenario>
#     <Title>
#     <H1>shitty title</H1>
#     </Title>
#     
#     <Subtitle>
#     <H2>shitty subtitle</H2>
#     </Subtitle>
#     
#     <Text>
#     sometext
#     </Text>
#   </Scenario>
#   <Scenario>
#       .
#       .
#       .
#   </Scenario>
#   ...
#   ...
#   ...
#   <Scenario>
#       .
#       .
#       .
#   </Scenario>
# </Scenarios>
# ```

# In[54]:


def listify_sign_posts(text):
    li = [s.strip() for s in text.splitlines()]
    root = etree.Element("sign_posts")
    for item in li:
        if item == "" or item == "\n":
            continue
        post = etree.Element("Sign-Post")
        post.text = item
        root.append(post)
    return root
        
def generate_scenario_xml(book):
    scenariosheet = book.worksheet("Scenarios")
    table = scenariosheet.get_all_values()
    df_scenarios = pd.DataFrame(table[2:], columns=table[0])
    
    # Build the XML tree
    root = etree.Element("Scenarios")
    
    for index, row in islice(df_scenarios.iterrows(), 0, None):
        scenario = etree.Element("Scenario")
        
        title = etree.Element("Title")
        h1 = etree.Element("H1")
        h1.text = sanitize_text(row[2])
        title.append(h1)
        scenario.append(title)
        
        subtitle = etree.Element("Subtitle")
        h2 = etree.Element("H2")
        h2.text =  sanitize_text(row[5])
        subtitle.append(h2)
        scenario.append(subtitle)
        
        text = etree.Element("Text")
        text.text = sanitize_text(row[7])
        scenario.append(text)
        
        #sign_posts = etree.Element("sign_posts")
        #sign_posts.text = generate_xml_list(sanitize_text(row[9]))
        scenario.append(listify_sign_posts(sanitize_text(row[9])))
        
        root.append(scenario)
        
    return etree.tostring(root).decode('utf-8')


# ## Ideas
# 
# Generate Ideas XML from excel sheet
# ```
# <Ideas>
#     <Idea>
#         <Title>
#             <H1>
#             </H1>
#         </Title>
#         <Subtitle>
#             <H2>
#             </H2>
#         </Subtitle>
#         <Value-Proposition-Canvas>
#             <Item>
#             </Item>
#             <Item>
#             </Item>
#         </Value-Proposition-Canvas>
#         <Value-Proposition-Text>
#             <Text>
#             </Text>
#         </Value-Proposition-Text>
#         ...
#         ...
#         ...
#     </Idea>
#     ...
#     ...
# </Ideas>
# ```  

# In[55]:


def listify_canvas(text, root_tag):
    li = [s.strip() for s in text.splitlines()]
    root = etree.Element(root_tag)
    for item in li:
        if item == "" or item == "\n":
            continue
        post = etree.Element("Item")
        post.text = item
        root.append(post)
    return root

def generate_ideas(book):
    ideasheet = book.worksheet("Ideation")
    table = ideasheet.get_all_values()
    df_ideas = pd.DataFrame(table[3:])#, columns=table[3])
    #print(df_ideas.head)
    #df_ideas.set_index('Title',inplace=True)
    df_ideas = df_ideas.transpose()
    df_ideas = df_ideas[1:]
    #print(df_ideas.shape)#['Title'])
    # Build the XML tree
    ideas = etree.Element("Ideas")
    
    for index, row in islice(df_ideas.iterrows(), 0, None):
        if (row[0]) == "":
            continue
        idea = etree.Element("Idea")
        
        # Title
        title = etree.Element("Title")
        heading1 = etree.Element("H1")
        heading1.text = row[0]
        title.append(heading1)
        idea.append(title)
        
        #subtitle
        sub = etree.Element("Subtitle")
        h2 = etree.Element("H2")
        h2.text = row[1]
        sub.append(h2)
        idea.append(sub)
        
        #intro
        intro = etree.Element("Intro")
        text = etree.Element("Text")
        text.text = row[2]
        intro.append(text)
        idea.append(intro)
        
        #Value Proposition_Canvas
        #vpc = etree.Element("Value_Proposition_Canvas")
        #text = etree.Element("text")
        #text.text = row[4]
        #vpc.append(listify_canvas(row[4], "Value_Proposition_Canvas"))
        idea.append(listify_canvas(row[4], "Value_Proposition_Canvas"))
        
        #Value Proposition_Text
        vpt = etree.Element("Value-Proposition-Text")
        text = etree.Element("Text")
        text.text = row[5]
        vpt.append(text)
        idea.append(vpt)        
        
        #Customer Relationships_Canvas
        #crc = etree.Element("Customer_Relationships_Canvas")
        #text = etree.Element("text")
        #text.text = row[6]
        #crc.append(text)
        idea.append(listify_canvas(row[6], "Customer-Relationships-Canvas"))  
        
        #Customer Relationships_Text
        crt = etree.Element("Customer-Relationships-Text")
        text = etree.Element("Text")
        text.text = row[7]
        crt.append(text)
        idea.append(crt)  
        
        #Channels_Canvas
        #cc = etree.Element("Channels_Canvas")
        #text = etree.Element("text")
        #text.text = row[8]
        #cc.append(text)
        idea.append(listify_canvas(row[8], "Channels-Canvas"))
        
        #Channels_Text
        ct = etree.Element("Channels-Text")
        text = etree.Element("Text")
        text.text = row[9]
        ct.append(text)
        idea.append(ct)
        
        #Key Resources_Canvas
        #krc = etree.Element("Key_Resources_Canvas")
        #text = etree.Element("text")
        #text.text = row[10]
        #krc.append(text)
        idea.append(listify_canvas(row[10], "Key-Resources-Canvas"))
        
        #Key Resources_Text
        krt = etree.Element("Key-Resources-Text")
        text = etree.Element("text")
        text.text = row[11]
        krt.append(text)
        idea.append(krt)
        
        #Key Activities_Canvas
        #kac = etree.Element("Key_Activities_Canvas")
        #text = etree.Element("text")
        #text.text = row[12]
        #kac.append(text)
        idea.append(listify_canvas(row[12], "Key-Activities-Canvas"))
        
        #Key Activities_Text
        kat = etree.Element("Key-Activities-Text")
        text = etree.Element("Text")
        text.text = row[13]
        kat.append(text)
        idea.append(kat)
        
        #Revenue Streams_Canvas
        #rsc = etree.Element("Revenue_Streams_Canvas")
        #text = etree.Element("text")
        #text.text = row[14]
        #rsc.append(text)
        idea.append(listify_canvas(row[14], "Revenue-Streams-Canvas"))
        
        #Revenue Streams_Text
        rst = etree.Element("Revenue-Streams-Text")
        text = etree.Element("Text")
        text.text = row[15]
        rst.append(text)
        idea.append(rst)
        
        #Key Partners_Canvas
        #kpc = etree.Element("Key_Partners_Canvas")
        #text = etree.Element("text")
        #text.text = row[16]
        #kpc.append(text)
        idea.append(listify_canvas(row[16], "Key-Partners-Canvas"))
        
        #Key Partners_Text
        kpt = etree.Element("Key-Partners-Text")
        text = etree.Element("Text")
        text.text = row[17]
        kpt.append(text)
        idea.append(kpt)
        
        #Customer Segmentation_Canvas
        #csc = etree.Element("Customer_Segmentation_Canvas")
        #text = etree.Element("text")
        #text.text = row[18]
        #csc.append(text)
        idea.append(listify_canvas(row[18], "Customer-Segmentation-Canvas"))
        
        #Customer Segmentation_Text
        cst = etree.Element("Customer-Segmentation-Text")
        text = etree.Element("Text")
        text.text = row[19]
        cst.append(text)
        idea.append(cst)
        
        #Cost Structure_Canvas
        #csc = etree.Element("Cost Structure_Canvas")
        #text = etree.Element("text")
        #text.text = row[20]
        #csc.append(text)
        idea.append(listify_canvas(row[20], "Cost-Structure-Canvas"))
        
        #Cost Structure_Text
        cst = etree.Element("Cost-Structure-Text")
        text = etree.Element("Text")
        text.text = row[21]
        cst.append(text)
        idea.append(cst)
        
        #Senario Fit_1
        sf = etree.Element("Senario-Fit-1")
        text = etree.Element("Text")
        text.text = row[23]
        sf.append(text)
        idea.append(sf)
        
        #Senario Fit_2
        sf = etree.Element("Senario-Fit-2")
        text = etree.Element("Text")
        text.text = row[24]
        sf.append(text)
        idea.append(sf)
        
        #Senario Fit_3
        sf = etree.Element("Senario-Fit-3")
        text = etree.Element("Text")
        text.text = row[25]
        sf.append(text)
        idea.append(sf)
        
        #Senario Fit_4
        sf = etree.Element("Senario-Fit-4")
        text = etree.Element("Text")
        text.text = row[26]
        sf.append(text)
        idea.append(sf)
        
        
        
        ideas.append(idea)
        # print(row[0])
        
    return etree.tostring(ideas).decode('utf-8')


# In[56]:


# print(generate_abbrevations(book))


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

# In[57]:


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

# In[58]:


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

# In[59]:


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


# # Run the pipeline

# In[60]:


def run():
    book = load_data_from_google_sheets()
    xml = ""
    # Add Abbreviations
    xml += generate_abbrevations(book)
    # Add Trends
    xml += generate_trends(book)
    # Add Scenarios
    xml += generate_ideas(book)
    # Add Ideation
    xml += generate_ideas(book)
    # Add Sources    
    # Replace the citation
    xml, authors = find_author_and_replace(xml)
    print(authors)
    xml += generate_sources(book, authors)
    # Wrap the root object arround all
    xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Root>\n' + xml + '</Root>'
    # print(xml)
    return xml


# In[61]:


# run()

