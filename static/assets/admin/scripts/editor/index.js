import $ from 'jquery';

var defaults = {
	translations: {},
	editorVersionSelector: '#editor_version',
	formEditorSelector: '#form-editor',
	titleSelector: '#form-editor #title',
	bodySelector: '#form-editor #body',
	extraBodySelector: '#form-editor #extra_body',
	btnSaveSelector: '.btn-save',
	sidebarStatusSelector: '#sidebar-status',
	statusSelector: '#form-editor #status',
};

// Class Constructor
function EditorPlugin(options) {
	this.options = $.extend({}, defaults, options || {});
	this.init();
}

EditorPlugin.prototype = {
	init: function() {
		var self = this;

		self.formEditor = $(self.options.formEditorSelector);
		self.editorVersion = $(self.options.editorVersionSelector);
		self.title = $(self.options.titleSelector);
		self.body = $(self.options.bodySelector);
		self.extraBody = $(self.options.extraBodySelector);
		self.btnSave = $(self.options.btnSaveSelector);

		self.sidebarStatus = $(self.options.sidebarStatusSelector);
		self.status = $(self.options.statusSelector);

		self.status.data('target', self.sidebarStatus);
		self.sidebarStatus.data('target', self.status);

		self.statusGroup = $(self.options.statusSelector + ',' + self.options.sidebarStatusSelector);

		self.setupForm();
		self.setupEditor();
		self.setupActions();
	},
	setupForm: function() {
		var self = this;

		if (!self.editorVersion.length || !self.extraBody.length) {
			return;
		}

		// transform the old format to the new one
		var txtSolutionEditorVersion = parseInt(self.editorVersion.val());

		if (txtSolutionEditorVersion === 0) {
			var text = self.extraBody.text();
			self.extraBody.text(
				$('<p>', {
					html: text.replace(/(?:\r\n|\r|\n)/g, '<br />')
				}).html()
			);
		}
	},
	setupEditor: function() {
		var self = this;

		if (!self.extraBody.length) {
			return;
		}

		var language = self.formEditor.data('language') || 'en';

		CKEDITOR.plugins.addExternal('confighelper', '/static/assets/libs/ckeditor/plugins/confighelper/', 'plugin.js');

		CKEDITOR.inline(self.extraBody.attr('id'), {
			height: 250,
			language: language,
			extraPlugins: 'divarea,confighelper',
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
			removeButtons: 'Underline,Strike,Subscript,Superscript,Anchor,Styles,Specialchar,About,Image,Table',
			format_tags: 'p;h2;h3;pre'
		});
	},
	setupActions: function() {
		var self = this;

		if (!self.btnSave.length) {
			return;
		}

		function isBlank(str) {
			return (!str || /^\s*$/.test(str));
		}

		self.btnSave.on('click', function(e) {
			e.preventDefault();
			var can = true;

			if (isBlank(self.title.val())) {
				notification.notify(self.options.translations.ERROR_STAMP_TITLE_EMPTY, 'error');
				can = false;
			}

			if (isBlank(self.body.val())) {
				can = false;
				notification.notify(self.options.translations.ERROR_STAMP_CHALLENGE_EMPTY, 'error');
			}

			// update ckeditor
			CKEDITOR.instances[self.extraBody.attr('name')].updateElement();

			if (isBlank(self.extraBody.val())) {
				can = false;
				notification.notify(self.options.translations.ERROR_STAMP_SOLUTION_EMPTY, 'error');
			}

			if (can) {
				self.formEditor.submit();
			}
		});

		self.statusGroup.on('change', function() {
			var value = this.value;
			var target = $(this).data('target');

			target.find('option[selected]').prop('selected', false);
			target.find('option[value=' + value + ']').prop('selected', true);
		});
	}
}

$(function() {
	defaults.translations = window.page_translations;
	var editor = new EditorPlugin(defaults);
});
