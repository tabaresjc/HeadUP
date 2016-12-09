define(['jquery'], function($) {
	'use strict';

	function Main(opt) {
		this.options = opt || {};
		this.setupElements();
		this.init();
	}

	Main.prototype = {
		setupElements: function() {
			// upload cover pictures elements
			this.coverPicInputFile = $('div.upload-file-container input[type=file]').first();
			this.coverPicContainer = $('div.cover-picture').first();
			this.picUpload = $('.cover-picture-edit-menu span.update, .cover-picture-edit-button span.upload');
			this.removePicture = $('.cover-picture span.delete').first();
		},
		init: function() {
			this.uploadCoverPictureSetup();
		},
		uploadCoverPictureSetup: function() {
			if (!this.coverPicInputFile.length || !this.coverPicContainer.length)
				return;
			var coverPicInputFile = this.coverPicInputFile,
				coverPicContainer = this.coverPicContainer,
				fileReader = new FileReader();

			// replace the background-image on the cover picture q4container
			fileReader.addEventListener('load', function(){
				//once the FileReader is loaded,
				coverPicContainer.addClass('with-picture')
					.css('background-image', 'url('+fileReader.result+')');
			}, false);

			// monitor any change on the input file
			coverPicInputFile.on('change', function() {
				var inputFile = coverPicInputFile.get(0);
				fileReader.readAsDataURL(inputFile.files[0]);

				coverPicContainer
					.addClass('with-picture')
					.removeClass('without-picture');
			});

			// trigger the input file to search for a picture
			this.picUpload.each(function(index, el) {
				$(el).click(function(e) {
					e.preventDefault();
					coverPicInputFile.trigger('click');
				});
			});

			this.removePicture.click(function(e) {
				e.preventDefault();
				var targetField = $($(this).data("target"));
				targetField.val("0");

				coverPicContainer.removeClass('with-picture')
					.addClass('without-picture')
					.css('background-image', 'none');
			});
		}
	};

	$(function() {
		// define the options used on the main script
		var options = {}
		var mainScript = new Main(options);
	});
});
