(function(window, document, $) {
	'use strict'

	$(function() {
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
				});

				// trigger the input file to search for a picture
				coverPicContainer.click(function(e) {
					e.preventDefault();
					coverPicInputFile.removeClass('with-picture')
						.trigger('click');
				});
			}
		};
		// define the options used on the main script
		var options = {}
		window.mainScript = new Main(options);
	});

}(window, document, jQuery));
