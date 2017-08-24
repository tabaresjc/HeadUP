define(['jquery'], function($) {
	'use strict';

	$(function() {
		var txtSolutionEditor = $('#txt_solution');

		if (txtSolutionEditor.length) {
			var txtSolutionEditorVersion = parseInt($('#editor_version').val());
			console.log(txtSolutionEditorVersion);
			if (txtSolutionEditorVersion === 0) {
				var text = txtSolutionEditor.text();

				txtSolutionEditor.text(
					$('<p>', {
						html: text.replace(/(?:\r\n|\r|\n)/g, '<br />')
					}).html()
				);
			}

			CKEDITOR.replace('txt_solution', {
				height: 250,
				extraPlugins: 'divarea',
				toolbarGroups: [{
					"name": "basicstyles",
					"groups": ["basicstyles"]
				}, {
					"name": "paragraph",
					"groups": ["list", "blocks"]
				}, {
					"name": "document",
					"groups": ["mode"]
				}, {
					"name": "insert",
					"groups": ["insert"]
				}, {
					"name": "styles",
					"groups": ["styles"]
				}],
				// Remove the redundant buttons from toolbar groups defined above.
				removeButtons: 'Underline,Strike,Subscript,Superscript,Anchor,Styles,Specialchar,About,Image,Table'
			});
		}

	});
});
