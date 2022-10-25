from . import ScraperBase

class ncode_syosetu_com(ScraperBase.ScraperBase):        
    def __init__(self, URL):
        super().__init__()
        self.URL = URL
        self.domain_URL = "https://ncode.syosetu.com/"
        self.tableOfContents = []
        self.tags = []
        self.remove_elements = []
        self.description = ""
        self.content_selector = ["xpath", "//div[@class='novel_view']"]

        self.bookTitle_selector = ["xpath", "//p[@class='novel_title']"]
        self.author_selector = ["xpath", "//div[@class='novel_writername']/a"]
        self.description_selector = ["xpath", "//div[@id='novel_ex']//text()"]
        self.tags_selector = []
        self.TOC_selector = ["xpath", "//div[@class='index_box']//a"]
        self.coverImage_selector = []
        self.chapterTitle_selector = ["class", 'novel_subtitle']
        self.next_selector = ["xpath", "//div[@class='novel_bn']/a[2]//@href"]

    def fetch_cover(self):
        return None