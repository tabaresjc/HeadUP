import $ from 'jquery';

function checkTos() {
	if ($('#check_tos').is(':checked')) {
		$('#submit-signup').removeAttr('disabled');
	} else {
		$('#submit-signup').attr('disabled', 'disabled');
	}
}

function setupTOS() {
	if ($('#check_tos').length) {
		$('#check_tos').change(function() {
			checkTos();
		});
		checkTos();
	}
}

function setupMenuFunctions() {
	// mobile side-menu slide toggler
	$('#sidebar-nav li.element').click(function(e) {
		e.stopPropagation();
	});

	$('#menu-toggler').click(function(e) {
		e.stopPropagation();
		$('body').toggleClass('menu');
	});

	$('body').click(function() {
		if ($(this).hasClass('menu')) {
			$(this).removeClass('menu');
		}
	});

	$('#dashboard-menu .dropdown-toggle').click(function(e) {
		e.preventDefault();
		var $item = $(this).parent();
		$item.toggleClass('current');
		if ($item.hasClass('current')) {
			$item.find('.submenu').slideDown('fast');
		} else {
			$item.find('.submenu').slideUp('fast');
		}
	});

	$(window).resize(function() {
		if ($(this).width() > 769) {
			$('body.menu').removeClass('menu')
		}
	});
}

function setupTooltips() {
	$('[data-toggle="tooltip"]').each(function(index, el) {
		$(el).tooltip({
			placement: $(this).data('placement') || 'right'
		});
	});
}

function setupStickySidebar() {
	var $sidebar = $('.col-sidebar-container'),
		$window = $(window),
		offset = $sidebar.offset(),
		topPadding = 15;

	if(!$sidebar.length) {
		return;
	}

	$window.scroll(function() {
		if ($window.scrollTop() > offset.top) {
			$sidebar.stop().animate({
				marginTop: $window.scrollTop() - offset.top + topPadding
			});
		} else {
			$sidebar.stop().animate({
				marginTop: 0
			});
		}
	});
}

$(function() {
	setupMenuFunctions();
	setupTooltips();
	setupTOS();
	setupStickySidebar();
});
