(function($, document, window, undefined) {
	'use strict';

	var alertify = require('alertifyjs');

	var pluginName = "huNotifications";

	// Create the defaults options
	var defaults = {
		// message selectors
		messageTextSelectors: '#message-list > div',
		// translate the category used on the system to the one use on this library
		messageTypes: {
			message: 'success',
			success: 'success',
			error: 'error',
			warning: 'warning'
		},
		notifierPosition: 'top-right',
		notifyWaitSeconds: 5
	};

	// Class Constructor
	function Notification(options) {
		this.options = $.extend({}, defaults, options);
		this.init();
	}

	Notification.prototype = {
		init: function() {
			this.setupSystemNotifications();
		},
		setupSystemNotifications: function() {
			// set the position of the notifier
			alertify.set('notifier', 'position', this.options.notifierPosition);
		},
		loadFlashMessages: function() {
			var main = this;
			var messagesEl = $(main.options.messageTextSelectors);

			messagesEl.each(function(index, element) {
				var category = $(element).data('category'),
					text = $(element).text();

				main.notify(text, category);
			});
		},
		notify: function(text, category, waitSeconds) {
			var main = this;
			var duration = waitSeconds || main.options.notifyWaitSeconds;
			var messageType = category !== undefined && typeof main.options.messageTypes[category] !== 'undefined' ? main.options.messageTypes[category] : 'success';
			alertify.notify(text, messageType, duration);
		}
	};

	var notification = new Notification();

	window[pluginName] = notification;

	$(function() {
		// load & display the system messages once the page is ready
		notification.loadFlashMessages();
	});

})(jQuery, document, window);
