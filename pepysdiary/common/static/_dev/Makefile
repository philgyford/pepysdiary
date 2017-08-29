# Assumes we have these python packages:
# * libsass
# * watchdog

BIN 		= ./node_modules/.bin

SASS_DIR	= ./sass
SASS_FILES  = $(SASS_DIR)/site.scss

CSS_DIR		= ../css
CSS_TARGET	= $(CSS_DIR)/site.css 

SASS_CMD	= sassc --style=compressed --sourcemap $(SASS_FILES) $(CSS_TARGET)

all: clean build-css

build-css: $(CSS_TARGET)

watch: watch-css

$(CSS_TARGET): $(SASS_FILES)
	@echo Compiling $@
	@$(SASS_CMD)

clean:
	@mkdir -p $(CSS_DIR)
	rm -f $(CSS_DIR)/*.css*


watch-css:
	@echo "Started watching CSS..."
	#watchmedo shell-command --patterns="*.scss" --recursive --command="sassc --style compressed sass/site.scss ../css/site.css" sass

	while sleep .5; do find $(SASS_DIR) -name "*css" -print | entr -d $(SASS_CMD); done



## Our CSS list (replaces .scss with .css in the list)
#CSS = $(SASS:.scss=.css) 

## Our minified CSS list
#CSS_MIN = $(CSS:.css=.min.css)

## Translate from .less to .css using the following command
## ($< = input file, $@ = output file)
#%.css: %.scss
    #$(SASSC) $< > $@

## The same as above, but with minification using the YUI CSS Compressor
#%.min.css: %.scss
    #$(SASSC) $< > $@
	#$(MINIFYCSS) @@

## This is our default target, so simply typing `make` will run this (dependency
## is the `dist` target)
#all: dist


## This target simply creates distribution versions of our JavaScript and CSS
## files
#dist: css-dist


## Here's the amazing part, this variable resolves to any outstanding
## sass -> css conversions depending on when each .scss file was last modified
#css: $(CSS)


## The same as above, except we clean up the generated combined CSS files after
## minifying
#css-dist: $(CSS_MIN)
    #rm -f $(CSS)


#clean:
	#rm -f $(CSS) $(CSS_MIN)

#.PHONY: js css

#../css/site.css: sass/site.scss
	#sassc sass/site.scss > ../css/site.css # 114710
	##sassc sass/site.scss > ../css/site.css --style compressed # 89263
	## Online minifier: 84383

