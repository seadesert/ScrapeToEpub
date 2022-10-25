from ebooklib import epub
from datetime import datetime
import re
from os.path import exists

class BookManager:
    def __init__(self):
        pass

    # Create eBook
    def create_book(self, metadata, chapters, save_directory):
        book = epub.EpubBook()

        if not metadata.get("title"):
            metadata['title'] = "Unknown Title"
        if not metadata.get("author"):
            metadata['author'] = "Unknown Author"
        if not metadata.get("language"):
            metadata['language'] = "en"
        if not metadata.get("description"):
            metadata['description'] = "Unknown Description"
        if not metadata.get("cover_image"):
            with open('./modules/default.jpg', 'br') as cover:
                image = cover.read()
            metadata['cover_image'] = image
        if not metadata.get("datetime"):
            metadata['datetime'] = datetime.now()

        # add metadata
        book.set_identifier(f'{metadata["title"]}_{metadata["author"]}_{metadata["datetime"]}')
        book.set_title(metadata['title'])
        book.set_language(metadata['language'])
        book.add_author(metadata['author'])
        book.add_metadata('DC', 'description', metadata['description'])
        book.add_metadata('DC', 'date', str(datetime.now()))
        book.set_cover("cover.jpg", metadata['cover_image'])


        # add stylesheet
        with open('./modules/style.css') as css:
            style = css.read()

        style_css = epub.EpubItem(uid="style_css", file_name="style/style.css", media_type="text/css", content=style)
        book.add_item(style_css)


        # add introduction
        intro = epub.EpubHtml(title='Introduction', file_name='intro.xhtml')
        intro.set_content(f"""
        <html>
            <body>
                <h1 id="epub-title">{metadata['title']} - {metadata['author']}</h1></br>
                <h3>Description</h3>
                <p>{metadata['description']}</p>
            </body>
        </html>
        """)
        book.add_item(intro)


        # add chapters
        epub_chapters = [intro, ]
        for title, chapter in chapters:
            chapter_filename = re.sub('[^\w_.)( -]', '_', title)
            chapter_filename = chapter_filename.replace(' ', '_')
            book_chapter = epub.EpubHtml(title=f'{title}',
                                         file_name=f"{chapter_filename.strip()}.xhtml")
            book_chapter.set_content(
                f"""
                    <center><h2 id="epub-title">{title}</h2></center></br>
                """
                + chapter)
            book_chapter.add_item(style_css)
            book.add_item(book_chapter)
            epub_chapters.append(book_chapter)


        # add Table of contents
        book.toc = (tuple(epub_chapters))

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())


        # add book spine
        book.spine = ['nav', ] + epub_chapters

        # create epub
        file_name = f"{metadata['title']}-{metadata['datetime']}.epub"
        file_name = re.sub('[^\w_.)( -]', '', file_name)

        epub.write_epub(f"{save_directory}/{file_name}", book)
        if exists(f"{save_directory}/{file_name}"):
            print("Task Completed", save_directory + file_name)
        else:
            print("Task Failed")
