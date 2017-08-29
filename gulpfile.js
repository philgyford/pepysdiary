'use strict';

var gulp = require('gulp');
var del = require('del');
var revAll = require('gulp-rev-all');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');

var sassDir = 'pepysdiary/common/static/src/sass';
var sassFiles = sassDir + '/**/*.scss';
var cssDir = 'pepysdiary/common/static/css';


gulp.task('clean', function() { 
  return del(cssDir + '/*.css.*');
});


gulp.task('sass', gulp.series('clean', function buildSass() {
  var sassOptions = {
    outputStyle: 'compressed',
    sourceComments: false
  };
  return gulp.src(sassFiles)
    .pipe(sourcemaps.init())
    .pipe(sass(sassOptions).on('error', sass.logError))
    .pipe(revAll.revision())
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(cssDir))
    .pipe(revAll.manifestFile())
    .pipe(gulp.dest(cssDir));
}));


gulp.task('sass:watch', function () {
  gulp.watch(sassFiles, gulp.series('sass'));
});


gulp.task('default', gulp.parallel('sass'));
gulp.task('watch', gulp.parallel('sass:watch'));
