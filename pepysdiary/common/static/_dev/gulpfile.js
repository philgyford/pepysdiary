'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');

var sassDir = './sass';
var sassFiles = sassDir + '/**/*.scss';
var cssDir = '../css';


gulp.task('sass', function () {
  var sassOptions = {
    outputStyle: 'compressed',
    sourceComments: false
  };
  return gulp.src(sassFiles)
    .pipe(sourcemaps.init())
    .pipe(sass(sassOptions).on('error', sass.logError))
    .pipe(sourcemaps.write(cssDir))
    .pipe(gulp.dest(cssDir));
});


gulp.task('sass:watch', function () {
  gulp.watch(sassFiles, ['sass']);
});


gulp.task('default', ['sass']);
gulp.task('watch', ['sass:watch']);
