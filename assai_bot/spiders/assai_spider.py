import scrapy
from requests_html import HTMLSession, HTML
# scrapy crawl assai -o items.json


class AssAI(scrapy.Spider):
    name = 'assai'
    base_url = 'https://anime47.com'
    search_url = 'https://myanimelist.net/search/all?q='
    page_number = 1
    start_urls = [
        'https://anime47.com/the-loai/doi-thuong-38/1.html'
    ]

    tags_dict = {
        'Hài Hước': 'Comedy',       'Đời Thường': 'Slice of life',  'Phiêu Lưu': 'Adventure',
        'Lịch Sử': 'Historical',    'Trinh Thám': 'Dectective',     'Kinh Dị': 'Horror',
        'Học Đường': 'School',      'Siêu Nhiên': 'Supernatural',   'Thể Thao': 'Sports',
        'Hành Động': 'Action',      'Âm Nhạc': 'Music',             'Phép Thuật': 'Magic',
        'Viễn Tưởng': 'Sci-Fi'
    }

    seasons_dict = {'Mùa Xuân ': "Spring ", "Mùa Hạ ": "Summer ", "Mùa Thu ": "Autumn ", "Mùa Đông ": "Winter "}

    def parse(self, response):
        """ Crawl data if it's an anime url """
        if response.url.find('phim') > 0:
            # Crawl anime's name
            name = response.css('.title-1::text').extract()[0]
            BD = name.find(' Blu')
            if BD > 0:
                name = name[:BD]
            transName = response.css('.title-2::text').extract()
            transName = transName[0] if transName else None

            # Crawl and handle the tags' format
            tags = response.css('.dd-cat a::text').extract()
            for i in range(len(tags)):
                tag = tags[i]
                if tag == 'Blu-ray':
                    tags = tags.remove(tag)
                if tag in self.tags_dict:
                    tags[i] = self.tags_dict.get(tag)

            # Crawl anime image link
            image_link = response.css('.movie-l-img img::attr(src)').extract()[0]

            # Crawl release date
            season = response.css('.movie-dd:nth-child(11) a::text').extract()
            season = season[0] if season else None
            date = response.css('.movie-dd:nth-child(14) a::text').extract()
            date = date[0] if season else None

            release_date = ''
            if season and date:
                for key in self.seasons_dict:
                    if key in season:
                        release_date += self.seasons_dict[key]

                release_date += date
            elif date:
                release_date = date
            else:
                release_date = 'Updating'

            # TODO: crawl the seasons and caching it in order not to recrawl

            """ Crawl some data on myanimelist.net """
            keyword = name.replace(' ', '-')
            myanimelist_search = self.search_url + str(keyword)
            session = HTMLSession()
            search_result = HTML(html=session.get(myanimelist_search).text).find(
                '.information.di-tc.va-t.pt4.pl8 a[href]', first=True)
            link = search_result.links.pop()
            html = HTML(html=session.get(link).text)

            # Crawl the description
            description = html.find('h2+ span', first=True).text

            # Crawl the transName if it's None
            if not transName:
                transName = html.find('h2+ .spaceit_pad',first=True).text
                if 'Synonyms: ' in transName:
                    transName = transName.replace('Synonyms: ', '')
                elif 'English: ' in transName:
                    transName = transName.replace('English: ', '')
                else:
                    transName = transName.replace('Japanese: ', '')

            # Crawl the producer, anime status and the number of episodes
            producer = episode = isCompleted = ''
            for e in html.find('div'):
                if e.find('span.dark_text', containing='Producers'):
                    producer = e.text.replace('Producers: ', '')
                if e.find('span.dark_text', containing='Episodes'):
                    episode = e.text.replace('Episodes: ', '')
                if e.find('span.dark_text', containing='Status'):
                    status = e.text.replace('Status: ', '')
                    isCompleted = 'YES' if 'Finished' in status else 'NO'

            producer = 'No info' if producer == 'None found, add some' else producer
            anime = {
                'name': name,
                'transName': transName,
                'producer': producer,
                'pictureLink': image_link,
                'tags': tags,
                'description': description,
                'seasons': [
                    {
                        'name': name,
                        'releaseDate': release_date,
                        'numberOfEpisode': episode,
                        'isCompleted': isCompleted,
                        'link': response.url,
                    }
                ]
            }
            yield anime

        """ Else, look for all the links in the page """
        count = 1
        for page in response.css('.movie-item.m-block'):
            link = page.css('a::attr(href)').extract()[0]
            link = link.replace('.', AssAI.base_url, 1)

            yield scrapy.Request(link, callback=self.parse)
            count += 1
            if count > 10:
                break

            # with open("items.json", "a") as f:
            #     f.write(title)
            #     f.close()

        """ Then move to the next page """
        # self.page_number += 1
        # if self.page_number < 17:
        #     # next_page = response.urljoin(str(self.page_number) + '.html')
        #     next_page = self.start_urls[0].replace('1.html', str(self.page_number) + '.html')
        #     yield Request(next_page, callback=self.parse)
