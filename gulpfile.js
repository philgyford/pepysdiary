/**
 * Gulpfile.
 * Defining the tasks that process files.
 */

var gulp        = require('gulp')
    concat      = require('gulp-concat'),
    del         = require('del'),
    rename      = require('gulp-rename'),
    replace     = require('gulp-replace'),
    rev         = require('gulp-rev'),
    sass        = require('gulp-ruby-sass'),
    uglify      = require('gulp-uglify'),
    usemin      = require('gulp-usemin'),
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
        },
        django: {
            templates: 'pepysdiary/templates/'
        }
    };

/***********************************************************************
 * Stuff we need to keep track of revisions and then update templates.
 */

/**
 * Keeps track of files that will have a cache-busting hash in their filename.
 * Will map something like:
 *  'site.css': 'site-be017230.css'.
 */
var revisions = {};

/**
 * Add an object to the revisions array.
 */
var addToRevisions = function(obj) {
    for (var source in obj) {
        revisions[source] = obj[source];
    };
};

/**
 * Called when other tasks have finished.
 * revisions should by then have some replacements to make.
 */
var updateTemplates = function(){
    gutil.log('Updating template');

    // To see what's in revisions now:
    gutil.log(revisions);

    gulp.src(paths.django.templates + 'common/base.html')
        // Only do the replacements if we have a replacement to do:
        .pipe('site.css' in revisions ? replace(/site\-[a-fA-F0-9]{8}\.css/, revisions['site.css']) : gutil.noop())
        .pipe('site' in revisions ? replace(/site\-[a-fA-F0-9]{8}\.min.js/, revisions['site']) : gutil.noop())
        .pipe(gulp.dest(paths.django.templates + 'common/'));
};


/***********************************************************************
 * The main tasks to run from the command line.
 * 
 * To add new tasks, add an entry in the "scripts" section of /package.json
 */

/**
 * Does everything to CSS and JS files one time.
 * Run with `npm run gulp`.
 */
gulp.task('default', ['js', 'js-copy', 'sass']);


/**
 * Does everything to CSS and JS files whenever they change.
 * Run with `npm run watch`.
 */
gulp.task('watch', function() {
    gulp.watch(paths.css.src + '**/*.scss', ['sass']);

    gulp.watch(paths.js.src + '*.js', ['js', 'js-copy']);
});


/***********************************************************************
 * Sub-tasks that are run by the main tasks (above).
 */

/**
 * Does the main JS stuff... minifies our JS, then concats several things.
 * Then removes temporary files.
 *
 * So, runs js-concat, which runs js-minify, then comes back here when done.
 */
gulp.task('js', ['js-concat'], function() {

    // Tidy up...
    del([paths.js.temp + 'pepys.min.js'],
        function(err) {
            gutil.log('Temporary JS files deleted');
        }
    );

    updateTemplates();
});

/*
 * Put the JS files we include on every page into one site.min.js file.
 * Must run js-concat first.
 * 
 * Creates revisioned files like site-d03917af.min.js
 * Deletes old revisioned files first.
 */
gulp.task('js-concat', ['js-minify'], function() {
    // First, we delete the old revisioned site file.
    del([paths.js.dest + 'site-*.min.js'],
        function(err) {
            gutil.log('Previous JS files deleted');
        }
    );

    // All the files to combine:
    return gulp.src([
        paths.js.src + 'vendor/jquery.min.js',
        paths.js.src + 'vendor/jquery.timeago.min.js',
        paths.js.src + 'vendor/bootstrap.min.js',
        paths.js.temp + 'pepys.min.js',
    ])
    // Into this filename:
    .pipe(concat('site'))
    // Add a unique hash to this revision:
    .pipe(rev())
    .pipe(rename({
        extname: ".min.js"
    }))
    // Save it:
    .pipe(gulp.dest(paths.js.dest))
    // Generate the manifest file that maps original to new filename.
    .pipe(rev.manifest())
    // Instead of saving it, parse the object in the file's content and save
    // it for later.
    .pipe(gutil.buffer(function(err, files){
        if (files.length > 0) {
            addToRevisions(JSON.parse(files[0].contents.toString()));
        };
    }));
});

/**
 * Minify our custom JS file, into a temporary file.
 * (3rd-party JS files are already minified.)
 * In a separate task so that the main 'js' one has to wait for it to complete
 * before continuing (I think).
 */
gulp.task('js-minify', function() {

    return gulp.src(paths.js.src + 'pepys.js')
        .pipe(uglify())
        .pipe(concat('pepys.min.js'))
        .pipe(gulp.dest(paths.js.temp));
});


/**
 * Copies a few vendor JS files from vendor to dest.
 * These are files which aren't used on every page, or need to be separate from
 * the main site.js
 *
 * They're already minified, so nothing else to do.
 * Not reliant on other processes.
 */
gulp.task('js-copy', [], function() {
    // Concat and copy the JS needed for <IE9 from src to dest.
    gulp.src([
        paths.js.src + 'vendor/html5shiv.min.js',
        paths.js.src + 'vendor/respond.min.js'
    ])
    .pipe(concat('lt-ie-9.min.js'))
    .pipe(gulp.dest(paths.js.dest));

    // Copy d3.js from src to dest.
    // (Just because it's tidier if all the JS we include on the site comes
    // from the same directory.)
    gulp.src([
        paths.js.src + 'vendor/d3.v3.min.js'
    ])
    .pipe(gulp.dest(paths.js.dest));
});


/**
 * Just calls our main SASS task and *then* does the update templates stuff.
 */
gulp.task('sass', ['sass-do'], function() {
    updateTemplates();
});

/**
 * SASSify our sass/site.scss file into css/site.css.
 *
 * Creates revisioned files like site-d03917af.css and site.css-d03917af.map
 * Deletes old revisioned files first.
 */
gulp.task('sass-do', function() {
    // First, we delete the old revisioned files.
    del([paths.css.dest + '*.css', paths.css.dest + '*.map'],
        function(err) {
            gutil.log('Previous CSS files deleted');
        }
    );

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


