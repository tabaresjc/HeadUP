/**
 * Miscellaneous functions to be used acroos the site
 * @return void
 */

define(['jquery', 'underscore'], function($, _) {
	'use strict';

	$('.vimeo-thumb').each(function() {
		$(this).smartVimeoEmbed(_({
			width: $(this).data('width')
		}).defaults({
			width: 640
		}));
	});

	var screenWidth = function() {
		return (window.innerWidth > 0) ? window.innerWidth : screen.width;
	};

	$(window).on('resize', _.debounce(function() {
		if (screenWidth() > 991) {
			$('#readable-navbar-collapse')
				.removeAttr('style')
				.removeClass('in');
		}
	}, 500));

	$('.js--toggle-search-mode').on('click', function(ev) {
		ev.preventDefault();

		$('body').toggleClass('search-mode');

		if ($('body').hasClass('search-mode')) {
			// set focus to the text field
			setTimeout(function() {
				$('.js--search-panel-text').focus();
			}, 10);

			// on escape key leave the search mode
			$(document).on('keyup.searchMode', function(ev) {
				ev.preventDefault();
				if (ev.keyCode === 27) {
					$('body').toggleClass('search-mode');
					$(document).off('keyup.searchMode');
				}
			});
		} else {
			$(document).off('keyup.searchMode');
		}
	});
});
