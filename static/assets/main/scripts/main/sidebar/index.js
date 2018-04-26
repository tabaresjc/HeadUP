import $ from 'jquery';
import _ from 'lodash';

const mediumScreenSize = 991;

function screenWidth() {
	return (window.innerWidth > 0) ? window.innerWidth : screen.width;
}

function updateSidebar() {
	var w = screenWidth(),
		sidebarWrapper = $('.sidebar-wrapper'),
		sidebarContainer = $('#main-sidebar');

	if (w > mediumScreenSize) {
		var ws = sidebarContainer.width();

		sidebarWrapper.css({
			'position': 'fixed',
			'width': ws +'px'
		});
	} else {
		sidebarWrapper.removeAttr('style');
	}
}

function onResize() {
	return _.debounce(function() {
		updateSidebar();
	}, 200);
}

$(window).on('resize', onResize);
$(window).on('load', updateSidebar);
