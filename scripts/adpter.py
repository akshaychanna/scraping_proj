from bs4 import BeautifulSoup
import requests
import pdb
import json
# from elasticsearch import Elasticsearch
# from elasticsearch import helpers
import logging
import pprint
import re

class Adpter(object):
    def __init__(self,url):
        self.url = url
        # self.es  = Elasticsearch(['http://localhost:9200/'], verify_certs=True)
        
    def process_target(self):
        data = requests.get(self.url)
        soup = BeautifulSoup(data.content, 'html.parser')
        all_divs = soup.find_all("div", class_="search-result")
        data_arr = []
        
        for i in all_divs:
            print("processing.......")
            obj = {}
            tag = i.find("div", class_ = "heading")
            if tag != None:
                obj['CompanyName'] = tag.get_text()
                obj['location'] =  (re.sub('\n\t','',i.find("div", class_="normal-detail").find("td" , text="Location").find_next_siblings()[0].get_text())).strip(": ")
                obj['website link'] = i.find("div", class_="normal-detail").find("td" , text="Website").find_next_siblings()[0].find("a").get("href")
                
                data = requests.get(obj["website link"])
                web_soup = BeautifulSoup(data.content, 'html.parser')
                obj["website"] = web_soup.find("div", class_= "detail-line").find("a").get_text()
                web_link = "https://"+obj["website"]
                
                try:
                    dom = requests.get(web_link,timeout=30)
                    contact_soup = BeautifulSoup(dom.content, 'html.parser')
                    aa = contact_soup.find("a",text="Contact Us")
                    btn = contact_soup.find("button",text="CONTACT US")
                    con = contact_soup.find("a",text="Contact")
                    span = contact_soup.find("span", text="CONTACT")
                    about = contact_soup.find("a",text="ABOUT US")
                    if aa != None:
                        if "http" in aa.get('href'):
                            obj["contact us link"] = aa.get('href')
                        else:
                            obj["contact us link"] = obj["website"]+aa.get('href')
                    elif btn != None:
                            if "http" in btn.parent.get('href'):
                                obj["contact us link"] = btn.parent.get('href')
                            else:
                                obj["contact us link"] = obj["website"]+btn.parent.get('href')
                    elif con != None:
                            if "http" in con.get('href'):
                                obj["contact us url"] = con.get('href')
                            else:
                                obj["contact us url"] = obj["website"]+con.get('href')
                    elif span != None:
                        if "http" in span.parent.get('href'):
                            obj["contact us link"] = span.parent.get('href')
                        else:
                            obj["contact us link"] = obj["website"]+span.parent.get('href')       
                    elif about != None:
                        if "http" in about.get('href'):
                            obj["contact us url"] = about.get('href')
                        else:
                            obj["contact us url"] = obj["website"]+about.get('href')
                except:
                    pass
                data_arr.append(obj)
        return data_arr
    
    
    # TO store scraped data into database uncomment below function , import statements and connection to ElasticSearch in __init__()
    # def add_data_to_es(self,bulk_data):
    #     resp = helpers.bulk(
    #         self.es,
    #         bulk_data,
    #         index = "startup_data",
    #         doc_type = "_doc"
    #     )

