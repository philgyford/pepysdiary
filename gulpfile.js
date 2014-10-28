/**
 * Gulpfile.
 * Defining the tasks that process files.
 */

var gulp = require('gulp')
    concat = require('gulp-concat'),
    sass = require('gulp-ruby-sass'),
    uglify = require('gulp-uglify');


gulp.task('default', ['js-concat', 'sass'], function() {
    //place code for your default task here
});


gulp.task('watch', function () {
    gulp.watch('pepysdiary/common/static/sass/**/*.scss', ['sass']);

    gulp.watch('pepysdiary/common/static/js/pepys.js',
                ['js-minify', 'js-concat']);
});


// Minify our custom JS file.
gulp.task('js-minify', function(cb) {
    gulp.src('pepysdiary/common/static/js/pepys.js')
        .pipe(uglify())
        .pipe(concat('pepys.min.js'))
        .pipe(gulp.dest('pepysdiary/common/static/js/'));
    // Callback, so next task knows this has finished.
    cb();
});


// Put the JS files we include on every page into one site.min.js file.
// Must run js-minify first.
gulp.task('js-concat', ['js-minify'], function() {
    return gulp.src([
        'pepysdiary/common/static/js/libs/jquery-1.11.0.min.js',
        'pepysdiary/common/static/js/libs/bootstrap.min.js',
        'pepysdiary/common/static/js/pepys.min.js',
    ])
    .pipe(concat('site.min.js'))
    .pipe(gulp.dest('pepysdiary/common/static/js/'));
});


gulp.task('sass', function () {
    gulp.src('pepysdiary/common/static/sass/**/*.scss')
        .pipe(sass({bundleExec: true, style: 'compressed'}))
        .pipe(gulp.dest('pepysdiary/common/static/css'));
});


