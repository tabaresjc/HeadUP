import alertify from 'Lib/alertifyjs/build/alertify.js';

(function($, document, window, undefined) {
	'use strict';

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
		},
		alert: function(message, title, onClickButton) {
			if (!message) {
				return;
			}
			alertify.alert(title || 'Warning', message, function() {
				if (typeof onClickButton === 'function') {
					onClickButton();
				}
			});
		}
	};

	var notification = new Notification();

	$(function() {
		// load & display the system messages once the page is ready
		notification.loadFlashMessages();
	});

	// CommonJS
	if (typeof module === 'object' && typeof module.exports === 'object') {
		module.exports = notification;
		// AMD
	} else if (typeof define === 'function' && define.amd) {
		define([], function() {
			return notification;
		});
		// window
	} else if (!window.notification) {
		window.notification = notification;
	}

})(jQuery, document, window);
