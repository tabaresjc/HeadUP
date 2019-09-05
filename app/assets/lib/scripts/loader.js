(function (window, document, $, undefined) {
	var loaderTemplate = '<div id="loader-wrapper" class="loaded"><div id="loader"><p class="loader-text">Please wait...</p><div class="loader"></div></div></div>';
	var loaderHtmlId = '#loader-wrapper';

	window.startLoader = function () {
		var loader = $(loaderHtmlId);

		if (!loader.length) {
			return;
		}

		loader.removeClass('loaded');
	};

	window.stopLoader = function () {
		var loader = $(loaderHtmlId);

		if (!loader.length) {
			return;
		}

		loader
			.removeClass('loaded')
			.addClass('loaded');
	};

	$(function () {
		$('body').append(loaderTemplate);
	});
}(window, document, jQuery));
