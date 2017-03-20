// include gulp
var gulp = require('gulp');

// include plugins
var jshint = require('gulp-jshint');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');

var mist_base = '.';
var sass_dir = mist_base + '/static/scss';
var sass_input = sass_dir + '/*.scss';
var css_dir = mist_base + '/static/dist/css';
var js_dir = mist_base + '/static/js';

gulp.task('lint', function() {
    return gulp
        .src(js_dir + '/*.js')
        .pipe(jshint())
        .pipe(jshint.reporter('default'));
});

gulp.task('sass', function() {
    return gulp
        .src(sass_input)
        .pipe(sass())
        .pipe(gulp.dest(css_dir));
});

// gulp.task('scripts', function() {
//     return gulp.src('').pipe();
// });

gulp.task('watch', function() {
    return gulp.watch(js_dir, ['lint', 'scripts']);
    return gulp.watch(sass_dir + '/*', ['sass']);
});

// gulp.task('', function() {
//     return gulp.src('').pipe();
// });

gulp.task('default', ['lint', 'sass']);
