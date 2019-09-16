(function($, document, window, undefined) {
	'use strict';

	// Create the defaults options
	var defaults = {
		btnSelector: '.upload-profile-picture-btn',
		formSelector: '.upload-profile-picture-form',
		inputFileSelector: 'input[type="file"]',
	};

	// Class Constructor
	function ProfileUploader(options) {
		this.options = $.extend({}, defaults, options);
	}

	ProfileUploader.prototype = {
		init: function() {
			if (this.loadElements()) {
				this.setupElements();
			}
		},
		loadElements: function() {
			this.btnSelector = $(this.options.btnSelector);
			if (!this.btnSelector.length) {
				return false;
			}
			this.formUploader = $(this.options.formSelector);
			this.fileInputHandler = this.formUploader.find(this.options.inputFileSelector).first();
			this.targetPicture = $(this.btnSelector.data('target'));

			if (!this.formUploader.length || !this.fileInputHandler.length || !this.targetPicture.length) {
				notification.alert('You need to setup the form for this plugin to work.', 'Profile Uploader Plugin');
				return false;
			}

			return true;
		},
		setupElements: function() {
			var main = this,
				fileReader = new FileReader();

			// replace the background-image on the cover picture q4container
			fileReader.addEventListener('load', function() {
				//once the FileReader is loaded,
				main.targetPicture.css('background-image', 'url(' + fileReader.result + ')');
			}, false);

			main.btnSelector.click(function(e) {
				e.preventDefault();
				main.fileInputHandler.trigger('click');
			});

			main.fileInputHandler.on('change', function() {
				var inputFile = main.fileInputHandler.get(0),
					form = main.formUploader.get(0);
				fileReader.readAsDataURL(inputFile.files[0]);
				var formData = new FormData(form);
				$.ajax({
				    url: main.btnSelector.attr('href'),  //Server script to process data
				    type: 'POST',
				    // Form data
				    data: formData,
				    contentType: false,
				    processData: false,
					success: function() {

					}
				});
			});
		}
	};

	var profileUploader = new ProfileUploader();

	$(function() {
		profileUploader.init();
	});

	// CommonJS
	if (typeof module === 'object' && typeof module.exports === 'object') {
		module.profileUploader = profileUploader;
		// AMD
	} else if (typeof define === 'function' && define.amd) {
		define([], function() {
			return profileUploader;
		});
		// window
	} else if (!window.profileUploader) {
		window.profileUploader = profileUploader;
	}

})(jQuery, document, window);
