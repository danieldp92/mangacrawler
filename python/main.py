import argparse
import os
import sys

from crawler.mangaworld import MangaworldCrawler, download_all
from utils import chapter_validator

def args_config():
    parser = argparse.ArgumentParser(description='Manga Crawler ')
    parser.add_argument('source', type=str, nargs=1,
                        help='It can contain the url of the manga or its name (in double quote)')

    parser.add_argument('-c', dest='chapter_number', type=int, help='Chapter number. It can be used only '
                                                                                 'when the source is the name of the '
                                                                                 'manga. By default, the program '
                                                                                 'download only the last number')
    parser.add_argument('-o', "--overwrite", dest='overwrite', action='store_true', help='Chapter number. It can be used only '
                                                                               'when the source is the name of the '
                                                                               'manga. By default, the program '
                                                                               'download only the last number')
    parser.add_argument('-a', '--all', action='store_true', help='If used when the name of the manga has been passed as '
                                                                'source, it downloads every chapter (it overrides the '
                                                                '-c functionality). If used with an url as source, '
                                                                'it will be ignored')
    parser.add_argument('-d', dest='dest_folder', help='Used to change the default destionation folder. The '
                                                                 'default output folder is the current directory of the'
                                                                 'script')

    return parser.parse_args()


if __name__ == '__main__':
    args = args_config()

    # Read all parameters
    source = args.source[0]
    all = args.all
    overwrite = args.overwrite
    chapter = args.chapter_number
    dest = args.dest_folder

    if dest is None:
        dest = os.getcwd()

    if source.startswith("http"):
        crawler = MangaworldCrawler(source)
        saved = crawler.download_and_save(source, overwrite=overwrite, dest=dest)
        if not saved:
            print("Chapter skipped (already in the selected folder)")
    else:
        download_all(source, all=all, chapter=chapter, overwrite=overwrite, dest=dest)

    print("\nBye!")


