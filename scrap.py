import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import math

class ProductScraper():
    def __init__(self):
        self.forumsearch_url = "http://www.webwinkelsoftware.nl/forum"
        self.pagesearch_url = "https://www.mcas.com.au/shop/category/?search_custom_category=&page={page}&per_page={item_num}&search_custom_partial_keyword="
        self.base_url = "http://www.webwinkelsoftware.nl"
    def scrape(self):
        # write csv headers
        # if os.path.exists('result.csv'):
        #     os.remove('result.csv')
        columns=['Forum', 'Name', 'Post', 'Replies']
        # df = pd.DataFrame(columns = columns)
        # df.to_csv('result.csv', mode='x', index=False, encoding='utf-8')

        # get forum urls
        response = requests.get(self.forumsearch_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        index = 0
        for item in soup.find_all('div', attrs= {'class': 'forum-category-item-title'}):
            tmp = item.find('a')
            index += 1
            if index < 9:
                continue
            if tmp != None:
                url= tmp.attrs['href'].strip()
                forum_name= self.get_forum_name(self.base_url+url)
                page_num= self.page_num(self.base_url+url)
                for page in range(1, page_num+1):
                    page_url= self.base_url+url+'/page:'+str(page)
                    response1= requests.get(page_url)
                    soup1= BeautifulSoup(response1.text, 'html.parser')
                    for topic_title_url_tmp in soup1.find_all('div', attrs= {'class': 'forum-topic-item-title'}):
                        topic_title_url= topic_title_url_tmp.find_all('a')[1].attrs['href'].strip()
                        new= self.scrape_post(self.base_url+topic_title_url).copy()
                        new.update({'Forum': forum_name})
                        print("I have inserted one column to csv now")
                        items= []
                        items.append(new)
                        # save datas in csv
                        df = pd.DataFrame(items, columns = columns)
                        df.to_csv('result.csv', mode='a', header=False, index=False, encoding='utf-8')
                    print('I have inserted one forum now')
        print('done')
                    
    def get_forum_name(self, url):
        response = requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        tmp= soup.find('div', attrs= {'class': 'user-data-container'})
        if tmp != None:
            forum_name= tmp.find('h2').text
            return forum_name
        return ""

    def page_num(self, url):
        response= requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        tmp= soup.find('div', attrs= {'class': 'paging-display'})
        page_num= 1
        if tmp!= None:
            if len(tmp.text.split())> 0:
                page_num= tmp.text.split()[-1]
        return int(page_num)
    def scrape_post(self, url):

        response= requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        name_tmp1= soup.find('div', attrs= {'class': 'user-details'})
        name= " "
        if name_tmp1!= None:
            name_tmp2= name_tmp1.find_all('a')
            if name_tmp2!= None:
                if len(name_tmp2)>2:
                    name= name_tmp2[1].text
        tmp= soup.find('div', attrs= {'class': 'user-post'})
        post= " "
        if tmp != None:
            tmp1= ""
            if tmp.find('h4') != None:
                tmp1= tmp.find('h4').text
            tmp4= ""
            if tmp.find('p')!= None:
                tmp4= tmp.find('p').text.replace('<br>', '\n')
            tmp5= ""
            if tmp.find('small')!= None:
                tmp5= tmp.find('small').text
            post= tmp1+'\n'+tmp4+'\n'+tmp5
        tmp2= soup.find('div', attrs= {'class': 'replies'})
        replies= " "
        if tmp2 != None:
            for reply in tmp2.find_all('div', attrs= {'class': 'topic-post'}):
                replies+= reply.find('small').text.split()[0]+ '\n'+reply.find('p').text+'\n'+reply.find('small').text.replace('<strong>', " ").replace('</strong>', "")+'\n'+'@messages@'+'\n'
        new= {'Name': '', 'Post': '', 'Replies': ''}
        new['Name']= name
        new['Post']= post
        new['Replies']= replies
        return new

if __name__ == '__main__':
    scraper = ProductScraper()
    scraper.scrape()