# Compass set-up for creating CSS files from the SASS files.
# Docs: http://compass-style.org/help/tutorials/configuration-reference/

# Require any additional compass plugins here.
require 'bootstrap-sass'

# Set this to the root of your project when deployed:
http_path = "/"
css_dir = "pepysdiary/common/static/css"
sass_dir = "pepysdiary/common/static/sass"
images_dir = "pepysdiary/common/static/css/img"
#javascripts_dir = "public/js"
#fonts_dir = "public/css/fonts"

relative_assets = true

# One of :expanded or :nested or :compact or :compressed
output_style = :compressed

# To enable relative paths to assets via compass helper functions. Uncomment:
# relative_assets = true

line_comments = false
