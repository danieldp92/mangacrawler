import os
import requests
import urllib.request
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class MangaCrawler(ABC):
    def __init__(self, url):
        self._url = url

        page = requests.get(url)
        self._soup = BeautifulSoup(page.content, 'html.parser')

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

        page = requests.get(self._url)
        self.soup = BeautifulSoup(page.content, 'html.parser')

    @property
    def soup(self):
        return self._soup

    @soup.setter
    def soup(self, value):
        self._soup = value

    @property
    def user_agent(self):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        return user_agent

    def download_and_save(self, name=None, chapter=None, overwrite=False, dest=os.getcwd()):
        """
        Download ana save a single chapter
        :param name: the name of the manga
        :param chapter: the chapter to dowload
        :param overwrite: true, if the content must be overwritten
        :param dest: the output folder
        :return: True, if the chapter has been downloaded, False otherwise
        """

        if name is None:
            name = self.get_name()

        if chapter is None:
            chapter = self.get_chapter()

        # Create manga chapter folder
        chapter_folder_name = name + " - Chapter " + str(chapter)
        chapter_dir = os.path.join(dest, chapter_folder_name)

        if os.path.exists(chapter_dir) and not overwrite:
            return False

        if not os.path.exists(chapter_dir):
            os.mkdir(chapter_dir)

        print("Processing the scan - \"{}\"...\n".format(chapter_folder_name))
        print("INFO")
        print("Manga name: {}".format(name))
        print("Chapter: {}\n".format(chapter))

        print("Scan detection...")
        urls_scan = self.get_all_scan()
        digits = len(str(len(urls_scan)))
        print("Number of scan found: {}".format(len(urls_scan)))

        print("Output folder: {}".format(chapter_dir))

        headers = {'User-Agent': self.user_agent}

        print("Downloading...")
        # Scrapes each scan page and save all the scan found
        for i in range(len(urls_scan)):
            page_number = str(i + 1).zfill(digits)
            src_img = urls_scan[i]

            img_ext = os.path.splitext(src_img)[1]
            img_name = page_number + img_ext
            img_path = os.path.join(chapter_dir, img_name)

            # Download and save the img url found
            request = urllib.request.Request(src_img, None, headers)  # The assembled request
            response = urllib.request.urlopen(request)
            data = response.read()

            with open(img_path, 'wb') as f:
                f.write(data)

        print("\nDownload completed")

        return True

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_chapter(self):
        pass

    @abstractmethod
    def get_number_pages(self):
        """
        Retrieve the number of pages of a manga's chapter
        :param url: the url of a manga's chapter
        :param soup: the soup object of the url of a manga's chapter
        :return: the number of pages of a manga's chapter
        """
        pass

    @abstractmethod
    def get_all_scan(self):
        """
        Analyze the page content of the url in order to find all the scan img url
        :param url: the url of the manga's chapter, containing the scan
        :return: a list of all the url scan
        """
        pass

