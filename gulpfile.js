/**
 * Gulpfile.
 * Defining the tasks that process files.
 */

var gulp        = require('gulp')
    concat      = require('gulp-concat'),
    del         = require('del'),
    rev         = require('gulp-rev'),
    sass        = require('gulp-ruby-sass'),
    uglify      = require('gulp-uglify'),
    gutil       = require('gulp-util');

var baseDir = 'pepysdiary/common/static/',
    paths = {
        css: {
            src:  baseDir + 'sass/',
            dest: baseDir + 'css/'
        },
        js: {
            src:  baseDir + 'js/src/',
            dest: baseDir + 'js/dist/',
            temp: baseDir + 'js/tmp/'
        }
    };

var revisions = {};

var addToRevisions = function(obj) {
    for (var source in obj) {
        revisions[source] = obj[source];
    };
};


/**
 * Does everything to CSS and JS files one time.
 */
gulp.task('default', ['js', 'sass'], function() {
    console.log(revisions);
});


/**
 * Does everything to CSS and JS files whenever they change.
 */
gulp.task('watch', function() {
    gulp.watch(paths.css.src+'*.scss', ['sass']);

    gulp.watch(paths.js.src+'*.js', ['js']);
});


/**
 * Our main JS task.
 * Must run js-concat first.
 * Which in turn must run js-minify first.
 * Finally we're back here and we:
 *  * Delete the temp file created by js-minify.
 *  * Copy JS files we only sometimes need into the dest directory.
 */
gulp.task('js', ['js-concat'], function() {

    del([paths.js.temp+'*.js'], function() {
        gutil.log('Temporary JS files deleted');
    });

    // NOTE: We need js-concat etc to finish before we copy these files below,
    // or else they might get deleted when old JS files are deleted.

    // Concat and copy the JS needed for <IE9 from src to dest.
    gulp.src([
        paths.js.src+'vendor/html5shiv.min.js',
        paths.js.src+'vendor/respond.min.js'
    ])
    .pipe(concat('lt-ie-9.min.js'))
    .pipe(gulp.dest(paths.js.dest));

    // Copy d3.js from src to dest.
    // (Just because it's tidier if all the JS we include on the site comes
    // from the same directory.)
    gulp.src([
        paths.js.src+'vendor/d3.v3.min.js'
    ])
    .pipe(gulp.dest(paths.js.dest));
});


/**
 * Put the JS files we include on every page into one site.min.js file.
 * Must run js-minify first.
 *
 * Creates revisioned files like site.min-d03917af.js
 * Deletes old revisioned files first.
 */
gulp.task('js-concat', ['js-minify'], function() {

    // First, we delete the old revisioned files.
    del(paths.js.dest+'*.js', function(err) {
        gutil.log('Previous JS files deleted');
    });

    // All the files to combine:
    return gulp.src([
        paths.js.src+'vendor/jquery.min.js',
        paths.js.src+'vendor/jquery.timeago.min.js',
        paths.js.src+'vendor/bootstrap.min.js',
        paths.js.temp+'pepys.min.js',
    ])
    // Into this filename:
    .pipe(concat('site.min.js'))
    // Add a unique hash to this revision:
    .pipe(rev())
    // Save it:
    .pipe(gulp.dest(paths.js.dest))
    // Generate the manifest file that maps original to new filename.
    .pipe(rev.manifest())
    // Instead of saving it, parse the object in the file's content and save
    // it for later.
    .pipe(gutil.buffer(function(err, files){
        addToRevisions(JSON.parse(files[0].contents.toString()));
    }));
});


/**
 * Minify our custom JS file, into a temporary file.
 * (3rd-party JS files are already minified.)
 */
gulp.task('js-minify', function() {

    return gulp.src(paths.js.src+'pepys.js')
        .pipe(uglify())
        .pipe(concat('pepys.min.js'))
        .pipe(gulp.dest(paths.js.temp));
});


/**
 * SASSify our sass/site.scss file into css/site.css.
 *
 * Creates revisioned files like site-d03917af.css and site.css-d03917af.map
 * Deletes old revisioned files first.
 */
gulp.task('sass', function() {

    // First, we delete the old revisioned files.
    del([paths.css.dest+'*.css', paths.css.dest+'*.map'], function(err) {
        gutil.log('Previous CSS files deleted');
    });

    // Our single main SCSS file (which @imports everything else).
    return gulp.src(paths.css.src+'site.scss')
        // Run SASS with options:
        .pipe(sass({bundleExec: true, style: 'compressed'}))
        // Add a unique hash to this revision:
        .pipe(rev())
        // Save it:
        .pipe(gulp.dest(paths.css.dest))
        // Generate the manifest file that maps original to new filename.
        .pipe(rev.manifest())
        // Instead of saving it, parse the object in the file's content and save
        // it for later.
        .pipe(gutil.buffer(function(err, files){
            addToRevisions(JSON.parse(files[0].contents.toString()));
        }));
});


