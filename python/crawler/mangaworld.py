import os
import requests
from urllib.parse import urlparse
import urllib.request
from bs4 import BeautifulSoup
import sys

# Local import
from crawler.crawler import MangaCrawler

mangaworld_archive = "https://www.mangaworld.cc/archive"


class MangaworldCrawler(MangaCrawler):
    def download_and_save(self, name=None, chapter=None, overwrite=False, dest=os.getcwd()):
        self.url = self.remove_page_url(self.url)
        return super().download_and_save(name=name, chapter=chapter, overwrite=overwrite, dest=dest)

    def get_name(self):
        if self.url is None:
            return None

        o = urlparse(self.url)
        return o.path.split("/")[3]

    """def get_volume(self, url=None, soup=None):
        if soup is None and url is None:
            return None

        if soup is None:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

        volume_select = soup.find("select", {"class": "volume custom-select"})
        volume_selected = volume_select.find("option", selected=True).text

        return volume_selected.split(" ")[1]"""

    def get_chapter(self):
        chapter_select = self.soup.find("select", {"class": "chapter custom-select"})
        chapter_selected = chapter_select.find("option", selected=True).text

        return chapter_selected.split(" ")[1]

    def get_number_pages(self, url=None, soup=None):
        page_select = self.soup.find("select", {"class": "page custom-select"})
        children = page_select.findChildren("option")
        return len(children)

    def get_all_scan(self):
        src_list = []

        # Detect the number of pages
        max_pages = self.get_number_pages()

        # Scrapes each scan page and save all the scan found
        for i in range(max_pages):
            page_number = str(i + 1)
            url_page = os.path.join(self.url, page_number).replace("\\", "/")

            page = requests.get(url_page)
            soup = BeautifulSoup(page.content, 'html.parser')

            # Parsing rules for the url of the scan
            src_img = soup.find("div", {"id": "page"}).find("img").get("src")
            src_list.append(src_img)

        return src_list

    @staticmethod
    def remove_page_url(url):
        """
        Remove the page from the mangaworld url, if presents
        :param url: the chapter url
        :return: the url without the page
        """
        # Check if there are some page references inside the url
        paths = os.path.split(url)
        page_number = paths[1]

        # If the page can be converted into int, it means that the url contains the page
        try:
            int(page_number)
            return paths[0]
        except:
            return url


def crawl_chapter_dict(url):
    if url is None:
        return None

    chapters = []

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    chapters_soup = soup.find("div", {"class": "chapters-wrapper py-2 pl-0"}).findAll("a", {"class": "chap"})
    for chapter_soup in chapters_soup:
        # TO DO: HANDLE INT EXCEPTION
        chapter = chapter_soup.find("span", {"class": "d-inline-block"}).text.split(" ")[1]
        try:
            chapter = int(chapter)
            url = chapter_soup.get("href")
            chapter_dict = {"chapter_number": chapter, "url": url}
            chapters.append(chapter_dict)
        except:
            try:
                chapter = float(chapter)
                url = chapter_soup.get("href")
                chapter_dict = {"chapter_number": chapter, "url": url}
                chapters.append(chapter_dict)
            except:
                print("Impossible to convert the following chapter \"{}\" in int".format(chapter))

    return chapters


def download_all(name, chapter=None, all=False, overwrite=False, dest=os.getcwd()):
    if name is None:
        print("Invalid name!!!")
        return

    name_quote = urllib.parse.quote(name.lower())
    url = mangaworld_archive + "?keyword=" + name_quote

    # Scrape of the url for finding all the manga options
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    manga_list = []
    manga_list_html = soup.findAll("a", {"class": "manga-title"})
    for manga_html in manga_list_html:
        name = manga_html.get("title")
        url = manga_html.get("href")
        manga = {"name": name, "url": url}
        manga_list.append(manga)

    # Menu cli option: show the menu if there are more refers. Output -> main url of the manga
    main_url = None
    if len(manga_list) > 1:
        print("There are multiple page under the name of \"{}\": please choose the right one\n".format(name))

        for i in range(len(manga_list)):
            print("Option {0}: {1}".format(str(i + 1), manga_list[i]["name"]))
            print("url: {}".format(manga_list[i]["url"]))

        option = input("Insert option: ")

        # Check if the option inserted is valid
        try:
            # Type checking
            option = int(option)
        except:
            print("Invalid option type. The value must be between 1 and {}".format(len(manga_list)))
            return

        if option <= 0 or option > len(manga_list):
            print("Invalid option type. The value must be between 1 and {}".format(len(manga_list)))
            return

        name = manga_list[option - 1]["name"]
        main_url = manga_list[option - 1]["url"]
    else:
        name = manga_list[0]["name"]
        main_url = manga_list[0]["url"]

    # Crawl the main url in order to find all info about chapters url
    chapters = crawl_chapter_dict(main_url)

    # All overrides the chapter selection
    if all:
        # Create a folder for all the chapters
        manga_dir = os.path.join(dest, name)
        if not os.path.exists(manga_dir):
            os.mkdir(manga_dir)

        for chapter_dict in chapters:
            crawler = MangaworldCrawler(chapter_dict["url"])
            saved = crawler.download_and_save(name=name, chapter=chapter_dict["chapter_number"], overwrite=overwrite,
                                              dest=manga_dir)
            if not saved:
                print("Chapter {} skipped (already in the selected folder)".format(chapter_dict["chapter_number"]))
            print("------------------------------------------------------")
    else:
        if chapter:
            try:
                chapter_dict = next(item for item in chapters if item["chapter_number"] == chapter)
            except:
                print("No chapter \"{}\" found".format(chapter))
                return

            crawler = MangaworldCrawler(chapter_dict["url"])
            saved = crawler.download_and_save(name=name, chapter=str(chapter), overwrite=overwrite, dest=dest)
            if not saved:
                print("Chapter {} skipped (already in the selected folder)".format(str(chapter)))
        else:
            last_chapter = max(chapters, key=lambda x: x['chapter_number'])
            print("Last scan detected: Chapter {}\n".format(last_chapter["chapter_number"]))
            choice = input("Do you want to dowload it? (Y/n): ")

            if choice.lower() == "y":
                crawler = MangaworldCrawler(last_chapter["url"])
                saved = crawler.download_and_save(name=name, chapter=last_chapter["chapter_number"],
                                                  overwrite=overwrite, dest=dest)
                if not saved:
                    print("Chapter {} skipped (already in the selected folder)".format(last_chapter["chapter_number"]))