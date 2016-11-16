(function($, document, window, undefined) {
	'use strict';

	// Create the defaults once
	var pluginName = "notifications";

	var defaults = {
		// parent selector
		parentSelector: 'body',
		// message selectors
		messageTextSelectors: '#message-list > div',
		// translate the category used on the system to the one use on this library
		messageTypes: {
			message: 'success',
			error: 'error',
			warning: 'warning'
		},
		notifierPosition: 'bottom-right',
	};

	// Class Constructor
	function Notification(options) {
		this.options = $.extend({}, defaults, options);
		this.init();
	}

	Notification.prototype = {
		init: function(element, options) {
			this.element = element;
			// Load the messages
			this.messageTextSelectors = $(this.options.parentSelector + ' ' + this.options.messageTextSelectors);

			this.setupSystemNotifications();
		},
		setupSystemNotifications: function() {
			// Load the types
			var messageTypes = this.options.messageTypes;
			// set the position of the notifier
			alertify.set('notifier', 'position', this.options.notifierPosition);

			this.messageTextSelectors.each(function(index, element) {
				var name = $(element).data('category'),
					text = $(element).text();
				var messageType = messageTypes[name];
				var notification = alertify.notify(text, messageType, 5);
			});
		}
	};

	// A really lightweight plugin wrapper around the constructor,
	// preventing against multiple instantiations
	$.fn[pluginName] = function(options) {
		return this.each(function() {
			if (!$.data(this, "plugin_" + pluginName)) {
				$.data(this, "plugin_" + pluginName, new Notification(this, options));
			}
		});
	};

	$(function() {
		// load & display the system messages once the page is ready
		$('#message-list').notifications();
	});

})(jQuery, document, window);
