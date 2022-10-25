import urllib3
from cssselect import GenericTranslator
from lxml.html.clean import Cleaner
from bs4 import BeautifulSoup
from lxml import etree
import http

# Scapper Parent Class - Overide the functions based on need.
class ScraperBase():
    def fetch_metadata(self):
        try:
            author = self.fetch_element(self.dom, self.author_selector).text
            bookTitle = self.fetch_element(self.dom, self.bookTitle_selector).text
            description = self.fetch_element(self.dom, self.description_selector)
            description = ''.join([str(s) for s in description])
            return {
                'title': bookTitle, 
                'author': author,
                'description': description,
                'cover_image': None
            }
        except:
            return None

    def fetch_cover(self):
        return http.request('GET', self.coverImage_link).data


    def fetch_chapters(self, chapter_dom):
        chapter_dom = chapter_dom[1]
        chapter_content = self.fetch_element(chapter_dom, self.content_selector)

        for ignore_element in self.remove_elements:
            for element in self.fetch_elements(chapter_content, ignore_element):
                element.getparent().remove(element)
        chapter_content = etree.tostring(chapter_content, encoding='utf-8', pretty_print=True, method="html").strip().decode('utf-8')
        chapter_title = self.fetch_element(chapter_dom, self.chapterTitle_selector).text
        return chapter_title, chapter_content


    def fetch_toc(self):
        tableOfContents = []
        table = self.fetch_elements(self.dom, self.TOC_selector)
        for element in table:
            title = element.text.strip()
            if self.domain_URL in element.attrib["href"]:
                url = element.attrib["href"]
            else:
                url = self.domain_URL + element.attrib["href"]

            chapter_resp = self.http.request('GET', url, headers=self.headers)
            chapter_soup = BeautifulSoup(chapter_resp.data, 'html.parser')
            chapter_dom = etree.HTML(str(chapter_soup).encode('utf-8'))
            tableOfContents.append((title, chapter_dom))
        return self.fetch_metadata(), tableOfContents

    def build_toc(self):
        current_URL = self.URL
        chapter_resp = self.http.request('GET', current_URL, headers=self.headers)
        chapter_soup = BeautifulSoup(chapter_resp.data, 'html.parser')
        chapter_dom = etree.HTML(str(chapter_soup).encode('utf-8'))
        
        title =  self.fetch_element(chapter_dom, ('xpath', '//title')).text
        tableOfContents = []

        while True:
            chapter_resp = self.http.request('GET', current_URL, headers=self.headers)
            chapter_soup = BeautifulSoup(chapter_resp.data, 'html.parser')
            chapter_dom = etree.HTML(str(chapter_soup).encode('utf-8'))
            try:
                next_URL = self.domain_URL + self.fetch_element(chapter_dom, self.next_selector).__str__()
                print("Traversing: ", current_URL)
            except IndexError:
                break
            if current_URL == next_URL:
                break

            tableOfContents.append((chapter_soup.title.string, chapter_dom))
            current_URL = next_URL
        return {'title': title}, tableOfContents

    def build_toc_single(self):
        current_URL = self.URL
        chapter_resp = self.http.request('GET', current_URL, headers=self.headers)
        chapter_soup = BeautifulSoup(chapter_resp.data, 'html.parser')
        chapter_dom = etree.HTML(str(chapter_soup).encode('utf-8'))
        title =  self.fetch_element(chapter_dom, ('xpath', '//title')).text
        tableOfContents = []
        tableOfContents.append((chapter_soup.title.string, chapter_dom))
        return {'title': title}, tableOfContents


    def __init__(self):
        self.http = urllib3.PoolManager()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'}

    # Fetch single element in urllib3
    def fetch_element(self, dom, selector):
        try:
            if selector[0] == "css":
                return dom.xpath(GenericTranslator().css_to_xpath(selector[1]))[0]
            elif selector[0] == "class":
                return dom.xpath(f"//*[@class='{selector[1]}']")[0]
            elif selector[0] == "tag":
                return dom.xpath(f"//{selector[1]}")[0]
            elif selector[0] == "link":
                return dom.xpath(f"//a[text()='{selector[1]}']")[0]
            elif selector[0] == "xpath":
                return dom.xpath(selector[1])[0]
            elif selector[0] == "id":
                return dom.xpath(f"//*[@id='{selector[1]}']")[0]
            elif selector[0] == "name":
                return dom.xpath(f"//*[@name='{selector[1]}']")[0]
        except:
            raise Exception("Unable to find chapter element! Check your url and mode.") 

    # Fetch multiple elements in urllib3
    def fetch_elements(self, dom, selector):
        if selector[0] == "css":
            return dom.xpath(GenericTranslator().css_to_xpath(selector[1]))
        elif selector[0] == "class":
            return dom.xpath(f"//*[@class='{selector[1]}']")
        elif selector[0] == "tag":
            return dom.xpath(f"//{selector[1]}")
        elif selector[0] == "link":
            return dom.xpath(f"//a[text()='{selector[1]}']")
        elif selector[0] == "xpath":
            return dom.xpath(selector[1])
        elif selector[0] == "id":
            return dom.xpath(f"//*[@id='{selector[1]}']")
        elif selector[0] == "name":
            return dom.xpath(f"//*[@name='{selector[1]}']")

    # Clean HTML
    def clean_html(self, chapter_content):
        cleaner = Cleaner()
        cleaner.safe_attrs = {'src', 'alt', 'href'}
        cleaner.annoying_tags = False
        cleaner.comments = False
        cleaner.add_nofollow = True
        cleaner.embedded = False
        cleaner.safe_attrs_only = True
        cleaner.remove_unknown_tags = True
        return cleaner.clean_html(chapter_content)