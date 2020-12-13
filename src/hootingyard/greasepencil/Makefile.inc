# Makefile.inc --- rules to be included into GreasePencil ebooks' Makefiles -*-Makefile-*-

# These variables must be defined by the including Makefile:
#
# BOOK = base filename for the book
# DATA = directory of XHTML book data
# OUTPUT = directory pdfs and ebooks are to be written to
# CODE = the GreasePencil scripts and templates directory
# WORKSPACE = the latex and epub scripts' working directories
#
# OUTPUT and WORKSPACE must be writable.

#------------------------------------------------------------------------------------------------

# The Makefile targets:

.phony :: default kindle lulu epub a4 clean

default : epub kindle lulu

lulu : $(OUTPUT)/$(BOOK).pdf
a4 : $(OUTPUT)/$(BOOK)-a4.pdf
epub : $(OUTPUT)/$(BOOK).epub
kindle : $(OUTPUT)/$(BOOK).mobi
clean : clean-ebook clean-latex


#------------------------------------------------------------------------------------------------

.phony :: test
test : lulu
	evince $(OUTPUT)/$(BOOK).pdf

#------------------------------------------------------------------------------------------------

# Make PDF files, via LuaTeX

LATEX=$(WORKSPACE)/$(BOOK)/latex

LATEX_FORMATS=$(CODE)/templates/latex-formats

LATEX_SOURCE= $(CODE)/templates/latex/*.tex \
              $(DATA)/Text/*.xhtml \
              $(DATA)/Images/*


$(OUTPUT)/$(BOOK).pdf : $(LATEX)/book-lulu.pdf
	mkdir -p $(OUTPUT)
	cp $(LATEX)/book-lulu.pdf $(OUTPUT)/$(BOOK).pdf

$(OUTPUT)/$(BOOK)-a4.pdf : $(LATEX)/book-a4.pdf
	mkdir -p $(OUTPUT)
	cp $(LATEX)/book-a4.pdf $(OUTPUT)/$(BOOK)-a4.pdf

define runtex
	python2.7 $(CODE)/validate-keyml.py $(CODE)/keyml.dtd $(DATA)/Text
	cp $(LATEX_FORMATS)/common.tex $(LATEX)/common.tex
	cd $(LATEX) ; rm -f book.toc book.aux book.idx book.log
	cd $(LATEX) ; lualatex -halt-on-error -file-line-error book
	cd $(LATEX) ; lualatex -halt-on-error -file-line-error book
endef

$(LATEX)/book-lulu.pdf : $(LATEX)/book.tex $(LATEX_FORMATS)/*.tex
	cp $(LATEX_FORMATS)/lulu.tex $(LATEX)/current.tex
	$(runtex)
	mv $(LATEX)/book.pdf $(LATEX)/book-lulu.pdf

$(LATEX)/book-a4.pdf : $(LATEX)/book.tex $(LATEX_FORMATS)/*.tex
	cp $(LATEX_FORMATS)/a4.tex $(LATEX)/current.tex
	$(runtex)
	mv $(LATEX)/book.pdf $(LATEX)/book-a4.pdf

$(LATEX)/book.tex : $(CODE)/xhtml-to-xetex.py $(LATEX_SOURCE)
	mkdir -p $(LATEX)
	python2.7 copy_images_for_latex.py $(DATA) $(CODE) $(LATEX)
	python2.7 $(CODE)/xhtml-to-xetex.py $(DATA) $(CODE) $(LATEX)

.phony :: clean-latex
clean-latex :
	python2.7 $(CODE)/rmdir.py "$(LATEX)"


#------------------------------------------------------------------------------------------------

# Make EPUB and Kindle ebooks

EBOOK=$(WORKSPACE)/$(BOOK)/ebook
EPUB=$(EBOOK)/epub

EBOOK_SOURCE= $(CODE)/templates/epub/* \
              $(DATA)/bookinfo.json \
              $(DATA)/Text/*.xhtml \
              $(DATA)/Images/* \
              $(DATA)/cover.png

$(OUTPUT)/$(BOOK).epub : $(EBOOK)/book.epub
	mkdir -p $(OUTPUT)
	cp $(EBOOK)/book.epub $(OUTPUT)/$(BOOK).epub

$(OUTPUT)/$(BOOK).mobi : $(EBOOK)/book.mobi
	mkdir -p $(OUTPUT)
	cp $(EBOOK)/book.mobi $(OUTPUT)/$(BOOK).mobi

$(EBOOK)/book.mobi : $(EBOOK)/book.epub
#	kindlegen $(EBOOK)/book.epub $(EBOOK)/book.epub | python2.7 $(CODE)/kindlegen-error-filter.py
	kindlegen $(EBOOK)/book.epub $(EBOOK)/book.epub

$(EBOOK)/book.epub : $(EBOOK)/touch
	python2.7 $(CODE)/validate-keyml.py $(CODE)/keyml.dtd $(DATA)/Text
	echo $(EPUB)
	echo $(EBOOK)
	rm -f $(EBOOK)/book.epub
	cd $(EPUB) ; zip -0Xqv $(EBOOK)/book.epub mimetype && zip -Xr9Dqv $(EBOOK)/book.epub META-INF OEBPS
	epubcheck $(EBOOK)/book.epub

$(EBOOK)/touch : $(CODE)/epub-copy-and-index.py $(EBOOK_SOURCE)
	python2.7 $(CODE)/rmdir.py "$(EPUB)"
	mkdir -p $(EPUB)/META-INF
	mkdir -p $(EPUB)/OEBPS/Text
	mkdir -p $(EPUB)/OEBPS/Images
	mkdir -p $(EPUB)/OEBPS/Styles
	mkdir -p $(EPUB)/OEBPS/Fonts
	cp $(CODE)/templates/epub/mimetype $(EPUB)/
	cp $(CODE)/templates/epub/container.xml $(EPUB)/META-INF/
	cp $(CODE)/fonts/*.ttf $(EPUB)/OEBPS/Fonts/
	cp $(DATA)/Styles/style.css $(EPUB)/OEBPS/Styles/style.css || cp $(CODE)/templates/epub/style.css $(EPUB)/OEBPS/Styles/style.css
	cp -R $(DATA)/cover.png $(EPUB)/OEBPS/Images/cover.png
	python2.7 $(CODE)/epub-copy-and-index.py $(DATA) $(CODE) $(EPUB)
	touch $(EBOOK)/touch

.phony :: clean-ebook
clean-ebook :
	python2.7 $(CODE)/rmdir.py "$(EPUB)"
	rm -f $(EBOOK)/book.epub
	rm -f $(EBOOK)/book.mobi
	rm -f $(EBOOK)/touch

#end
