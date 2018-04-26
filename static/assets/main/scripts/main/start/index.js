import $ from 'jquery';
import _ from 'lodash';

const mediumScreenSize = 991;
var elementId = location.hash;

function screenWidth() {
	return (window.innerWidth > 0) ? window.innerWidth : screen.width;
};

function onResize() {
	return _.debounce(function() {
		var w = screenWidth();
		if (w > mediumScreenSize) {
			$('#readable-navbar-collapse')
				.removeAttr('style')
				.removeClass('in');
		}
	}, 200);
}

function stopScrolling() {
	if (location.hash) {
		elementId = location.hash;
		window.scrollTo(0, 0);
	}
}

function scrollToElement() {
	if (elementId && $(elementId).length) {
		var y = $(elementId).offset().top - 80;
		$(document).scrollTop(y);
	}
}

setTimeout(stopScrolling, 0);

$(function() {
	setTimeout(scrollToElement, 0);
});

$(window).on('resize', onResize);
