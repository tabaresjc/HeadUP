define(['jquery', 'underscore'], function($, _) {
	'use strict';

	var screenWidth = function() {
		return (window.innerWidth > 0) ? window.innerWidth : screen.width;
	};

	function stickySidebar() {
		var w = screenWidth(),
			sidebarWrapper = $('.sidebar-wrapper'),
			sidebarContainer = $('#main-sidebar');

		if (w > 991) {
			var ws = sidebarContainer.width();

			sidebarWrapper.css({
				'position': 'fixed',
				'width': ws +'px'
			});
		} else {
			sidebarWrapper.removeAttr('style');
		}
	}

	$(window).on('resize', _.debounce(function() {
		var w = screenWidth();
		if (w > 991) {
			$('#readable-navbar-collapse')
				.removeAttr('style')
				.removeClass('in');
		}
		stickySidebar();
	}, 200));

	$(function() {
		stickySidebar();

		$('.vimeo-thumb').each(function() {
			$(this).smartVimeoEmbed(_({
				width: $(this).data('width')
			}).defaults({
				width: 640
			}));
		});

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
});
