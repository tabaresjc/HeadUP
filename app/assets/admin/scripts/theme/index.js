import $ from 'jquery';

function setupSignup() {
	if (!$('#check_tos').length || !$('#submit-signup').length) {
		return;
	}

	var checkTOS = function () {
		if ($('#check_tos').is(':checked')) {
			$('#submit-signup')
				.removeAttr('disabled')
				.removeClass('disabled');
		} else {
			$('#submit-signup')
				.attr('disabled', 'disabled')
				.addClass('disabled');
		}
	};

	var onSignupBtnClick = function (e) {
		e.preventDefault();
		var gtagToken = $(this).data('gtag');

		if (typeof window.startLoader === 'function') {
			window.startLoader();
		}

		if (gtagToken && typeof window.gtag === 'function') {
			window.gtag('event', 'conversion', {
				'send_to': gtagToken,
				'event_callback': submitForm
			});

			setTimeout(function () {
				submitForm();
			}, 2000);
		} else {
			submitForm();
		}
	};

	$('#check_tos').change(checkTOS);
	$('#submit-signup').on('click', onSignupBtnClick);

	checkTOS();
}

function submitForm() {
	if ($('#submit-signup-form').data('busy') !== '1') {
		$('#submit-signup-form').submit();
		$('#submit-signup-form').data('busy', '1');
	}
}

function setupMenuFunctions() {
	// mobile side-menu slide toggler
	$('#sidebar-nav li.element').click(function (e) {
		e.stopPropagation();
	});

	$('#menu-toggler').click(function (e) {
		e.stopPropagation();
		$('body').toggleClass('menu');
	});

	$('body').click(function () {
		if ($(this).hasClass('menu')) {
			$(this).removeClass('menu');
		}
	});

	$('#dashboard-menu .dropdown-toggle').click(function (e) {
		e.preventDefault();
		var $item = $(this).parent();
		$item.toggleClass('current');
		if ($item.hasClass('current')) {
			$item.find('.submenu').slideDown('fast');
		} else {
			$item.find('.submenu').slideUp('fast');
		}
	});

	$(window).resize(function () {
		if ($(this).width() > 769) {
			$('body.menu').removeClass('menu')
		}
	});
}

function setupTooltips() {
	$('[data-toggle="tooltip"]').each(function (index, el) {
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

	if (!$sidebar.length) {
		return;
	}

	$window.scroll(function () {
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

function scanOembed() {
	let elements = document.querySelectorAll('oembed[url]');

	if (!elements || !elements.length) {
		return;
	}

	elements.forEach(element => {
		let url = element.attributes.url.value;
		let params = {
			url: url
		};
		$.getJSON('/api/oembed/item',
			params,
			function (response) {
				let data = response.data;

				if (!data.response || data.url !== url) {
					return;
				}

				if (!data.response.html) {
					return;
				}

				let container = document.createElement('div');
				container.innerHTML = data.response.html;
				container = container.childNodes[0];

				container.removeAttribute('height');
				container.removeAttribute('width');

				element.parentNode.replaceChild(container, element);
			});
	});
}

$(function () {
	setupSignup();
	setupMenuFunctions();
	setupTooltips();
	setupStickySidebar();
	scanOembed();
});
