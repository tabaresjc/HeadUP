jQuery(document).ready(function($) {
	WPGFunctions = {
		setup: function() {
			$('#txt_editor_area').ckeditor();
			$('#btn_editor_clear').click(WPGFunctions.clearTextArea);
		},
		clearTextArea: function() {
			$('#txt_editor_area').val('');
			return true;
		},
		setErrorMessage: function(message){
			$('#pad-wrapper .alert').remove();
			$('#pad-wrapper').prepend('<div class="alert alert-danger"><i class="icon-remove-sign"></i>'+message+'</div>');
		},
		testEmptyString: function(str) {
			return (!str || /^\s*$/.test(str));
		}
	}
	$(WPGFunctions.setup);
});

