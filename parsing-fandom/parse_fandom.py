import bs4
import requests

import sys
import time
import json

BASE_LINK = 'https://{fandom}.fandom.com'
START_GALLERY_LINK = 'https://{fandom}.fandom.com/wiki/Special:AllPages?from='


class GalleryParser:
    def __init__(self, fandom):
        self._fandom = fandom
        self._start_link = START_GALLERY_LINK.format(fandom=fandom)
        self._base_link = BASE_LINK.format(fandom=fandom)
        self._gallery_links = set()
        self._content_links = []

    def get_link(self, a_node):
        return f'{self._base_link}{a_node.attrs["href"]}'
    
    def _get_next_gallery(self, soup):
        attrs = {'class': 'mw-allpages-nav'}
        nodes = soup.find_all('div', **attrs)[0].find_all('a')

        next_gallery_url = None
        for node in nodes:
            if node.text.startswith('Next page'):
                next_gallery_url = self.get_link(node)

        if next_gallery_url is None:
            return

        if next_gallery_url in self._gallery_links:
            return
    
        return next_gallery_url
    
    def _pull_out_content_links(self, soup):
        attrs = {'class': 'mw-allpages-body'}
        nodes = soup.find_all('div', **attrs)[0].find_all('a')
        for node in nodes:
            link = self.get_link(node)
            if not link.endswith('Image_Gallery') and not link.endswith('Main_Page') and not link.endswith('_Wiki'):
                self._content_links.append(link)

    def _parse_gallery(self, url):
        self._gallery_links.add(url)
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, 'html5lib')

        self._pull_out_content_links(soup)
        
        next_gallery_url = self._get_next_gallery(soup)
        if next_gallery_url is not None:
            time.sleep(0.1)
            self._parse_gallery(next_gallery_url)

    def parse(self):
        self._parse_gallery(self._start_link)
        return self._content_links


class PostParser:
    def __init__(self, content_links):
        self._content_links = content_links

    def _get_name(self, soup):
        name = soup.find(**{'class': 'mw-page-title-main'})
        return name.string if name else 'None'
    
    def _get_properties(self, aside):
        properties = {}
        fields = aside.find_all('h3')
        for field in fields:
            key = field.string
            field_value = field.find_next_sibling('div')
            properties[key] = field_value.string
        return properties
    
    def _get_string_from_tag(self, node):
        strings = ['']
        for node in node.children:
            if node.name in ('aside', 'table', 'br'):
                strings.append('\n')
                continue
            if isinstance(node, bs4.NavigableString):
                strings.append(node)
            else:
                strings.append(self._get_string_from_tag(node))
        return ''.join(strings)

    def _get_content(self, main_node):
        content = [[]]
        for tag in main_node.children:
            if tag.name in ('aside', 'table', 'div', 'br', 'ul'):
                content[-1].append('')
                continue

            if isinstance(tag, bs4.Comment):
                content[-1].append('')
                continue

            if tag.name == 'h2':
                content[-1].append('')
                header = self._get_string_from_tag(list(tag.children)[0])
                if header == 'Navigation':
                    break
                if header:
                    content.append([header])
                continue

            if tag.name == 'p':
                content[-1].append('')
                content[-1].append(self._get_string_from_tag(tag))
                content[-1].append('')
                continue

            if not content[-1]:
                content[-1].append('')

            if isinstance(tag, bs4.NavigableString):
                content[-1][-1] += tag
            else:
                content[-1][-1] += self._get_string_from_tag(tag)

        result = []
        for idx, block in enumerate(content):
            lines = [line.strip() for line in block if line.strip()]
            if idx and len(lines) == 1:
                continue
            if lines:
                result.append(lines)

        return result
    
    def _parse_synopsis(self, main_node):
        content_nodes = main_node.find_all(**{'class': 'wds-tab__content'})
        content = []
        for content_node in content_nodes:
            content += self._get_content(content_node)
        return content

    def _pasre_post(self, link):
        try:
            print('parsing:', link)
            response = requests.get(link)
            soup = bs4.BeautifulSoup(response.text, 'html5lib')
            result = {}
            main_node = soup.find('div', **{'class': 'mw-parser-output'})
            if main_node is None:
                return None

            result['name'] = self._get_name(soup)
            result['link'] = link
            if link.endswith('Synopsis'):
                result['content'] = self._parse_synopsis(main_node)
                return result

            aside = main_node.find('aside')
            if aside:
                result['properties'] = self._get_properties(aside)
            result['content'] = self._get_content(main_node)
        except:
            print("Error during parsing", link, file=sys.stderr)
            raise
        return result

    def parse(self):
        result = []
        for link in self._content_links:
            post = self._pasre_post(link)
            if post:
                result.append(post)
            time.sleep(0.1) 
        return result
    

def main():
    gallery_parser = GalleryParser(sys.argv[1])
    content_links = gallery_parser.parse()
    print('pages:', len(content_links))
    post_parser = PostParser(content_links)
    posts = post_parser.parse()
    with open('result.json', 'w') as f:
        json.dump(posts, f)


if __name__ == '__main__':
    main()
    # print(PostParser([])._pasre_post('https://rezero.fandom.com/wiki/Re:Zero_Episode_14'))
