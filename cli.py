import click
import os
from urllib.parse import urlparse
import importlib

from pkg_resources import require
from modules.BookManager import BookManager
from modules.ScraperBase import ScraperBase


@click.command()
@click.argument('url')
@click.argument('dir', required=False)
@click.option('-s', '--single', is_flag=True)
def main(url, dir, single):
    click.echo("Scraping {}".format(url))
    scraper_list = os.listdir('modules')
    domain = urlparse(url).netloc
    module_name = domain.replace('.', '_')

    if module_name+'.py' in scraper_list:
        click.echo("Scraper for Domain {} Found!".format(domain))
        module = importlib.import_module(f'modules.{module_name}')
        scraper = getattr(module, module_name)
        instance = scraper(url)

        if not single:
            metadata, table_of_contents = instance.fetch_toc()
            metadata = instance.fetch_metadata()
            if len(table_of_contents) == 0:
                metadata, table_of_contents = instance.build_toc()
            print(len(table_of_contents), "- Chapters detected!")
        else:
            metadata, table_of_contents = instance.build_toc_single()

        chapters = []
        for chapter_dom in table_of_contents:
            chapter_title, chapter_content = instance.fetch_chapters(chapter_dom)
            chapters.append((chapter_title, chapter_content))
        
        bm = BookManager()
        if dir:
            bm.create_book(metadata=metadata, chapters=chapters, save_directory=dir)
        else:
            bm.create_book(metadata=metadata, chapters=chapters, save_directory='./')

    else:
        click.echo("Create a new scraper for Domain {}\n".format(domain))


if __name__ == "__main__":
    main()