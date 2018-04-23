define(['jquery', 'underscore'], function($, _) {
	'use strict';

	var mediumScreenSize = 991;

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

	$(window).on('resize', onResize);
});
