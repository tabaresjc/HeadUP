'use strict';

import { AppConfig } from 'Assets/main/scripts/appConfig';
import { StoryApiService, CategoryApiService } from 'Assets/main/scripts/api';
import { SpinnerHelper } from 'Assets/helpers';
import { ImageUploadAdapterPlugin } from './upload';
import { CoverPicturePlugin } from './cover-picture';
import $ from 'jquery';
import Choices from 'choices.js';

export class StoryEditorComponent {

	constructor(options) {
		this._moduleId = 'story-editor-page';
		this._options = Object.assign({
			containerId: 'story-container',
			titleId: 'story-title',
			bodyId: 'story-body',
			publishId: 'story-publish',
			saveDraftId: 'story-save-draft',
			categorySelectId: 'story-category',
			launchDialogBtnId: 'story-launch-modal',
			dialogId: 'story-dialog',
			anonymousCheckboxId: 'anonymous-checkbox',
			cancelBtnId: 'story-cancel',
			messages: {
				beforeUnload: `You have unfinished changes, do you wish to leave?`
			}
		}, options || {});

		this._hasChanged = false;
	}

	onLoad() {
		this.start();
	}

	start() {
		const pageContainer = document.getElementById(this._moduleId);

		// check if current page match the id of this module
		if (!pageContainer) {
			return;
		}

		if (!this._options.titleId || !this._options.bodyId) {
			console.warn(`[HUP] unable to initialize editor`);
			return;
		}

		this._storyContainer = document.getElementById(this._options.containerId);
		this._storyApiService = new StoryApiService();
		this._categoryApiService = new CategoryApiService();
		this._spinnerHelper = new SpinnerHelper();
		this._titleTxt = document.getElementById(this._options.titleId);
		this._bodyTxt = document.getElementById(this._options.bodyId);
		this._categorySel = document.getElementById(this._options.categorySelectId);
		this._anonymousCheckbox = document.getElementById(this._options.anonymousCheckboxId);

		if (!this._storyContainer || !this._titleTxt || !this._bodyTxt) {
			console.warn(`[HUP] editor can't be initialized`);
			return;
		}

		const promises = [
			this._setupTitle(),
			this._setupBody(),
			this._getStory(),
			this._getCategories()
		];

		this._spinnerHelper.start();

		Promise.all(promises)
			.then(values => {
				// assign the results of each promise
				[
					this._titleEditor,
					this._bodyEditor,
					this._story,
					this._categoryData
				] = values;

				this._titleEditor.setData(this._story.title || '');

				let body = this._story.extra_body || '';

				if (this._story.body) {
					body = `<h3>${this._story.body}</h3>${body}`;
				}

				this._bodyEditor.setData(body);
				this._categoryChoice = this._buildStoryChoice(
					this._categoryData.items,
					this._story);

				this._coverPicture = new CoverPicturePlugin({
					picture: this._story.cover_picture,
					post_id: this._story.id,
				});

				this._setupListeners();

				console.info(`[HUP] editor initialized`);
				this._spinnerHelper.stop();
			})
			.catch(error => {
				console.error(error.stack);
				this._spinnerHelper.stop();
			});
	}

	_setupTitle() {
		const config = {
			placeholder: this._titleTxt.getAttribute('data-placeholder'),
			language: this._getLanguage(),
			blockToolbar: [],
			balloonToolbar: [],
			plugins: ['Essentials', 'Paragraph']
		};

		return window.BalloonEditor.create(this._titleTxt, config);
	}

	_setupBody() {
		const config = {
			placeholder: this._bodyTxt.getAttribute('data-placeholder'),
			language: this._getLanguage(),
			extraPlugins: [ImageUploadAdapterPlugin],
			heading: {
				options: [
					{ model: 'paragraph', title: 'P', class: 'ck-heading_paragraph' },
					{ model: 'heading3', view: 'h3', title: 'T1', class: 'ck-heading_heading3' },
					{ model: 'heading4', view: 'h4', title: 'T2', class: 'ck-heading_heading4' },
					{ model: 'heading5', view: 'h5', title: 'T3', class: 'ck-heading_heading5' },
					{ model: 'heading6', view: 'h6', title: 'T4', class: 'ck-heading_heading5' }
				]
			}
		};

		return window.BalloonEditor.create(this._bodyTxt, config);
	}

	_setupListeners() {
		this._launchDialgoBtn = document.getElementById(this._options.launchDialogBtnId);
		this._launchDialgoBtn.addEventListener('click', this._launchDialog.bind(this));

		this._publishBtn = document.getElementById(this._options.publishId);
		this._publishBtn.addEventListener('click', this._publishStory.bind(this));

		this._saveDraftBtn = document.getElementById(this._options.saveDraftId);
		this._saveDraftBtn.addEventListener('click', this._saveDraft.bind(this));

		this._cancelBtn = document.getElementById(this._options.cancelBtnId);
		this._cancelBtn.addEventListener('click', this._cancel.bind(this));

		this._titleEditor.model.document.on('change:data', () => {
			this._hasChanged = true;
		});

		this._bodyEditor.model.document.on('change:data', () => {
			this._hasChanged = true;
		});

		window.addEventListener('beforeunload', (event) => {
			if (this._hasChanged) {
				event.returnValue = this._options.messages.beforeUnload;
			}
		});
	}

	_publishStory(evt) {
		evt.preventDefault();

		const id = this._story.id;
		const data = this._getData();

		// close the dialog
		this._getModalDialog().modal('hide');

		if (!this._validate()) {
			return;
		}

		if (!id || !data) {
			return false;
		}

		this._updateStatus(false);

		this._storyApiService.publish(id, data)
			.then(response => {
				this._updateStatus(true);
				this._hasChanged = false;

				if (response.redirect_to) {
					window.location = response.redirect_to;
				}
			})
			.catch(error => {
				this._updateStatus(true);
			});
	}

	_saveDraft(evt) {
		evt.preventDefault();

		const id = this._story.id;
		const data = this._getData();

		if (!id || !data) {
			return false;
		}

		this._updateStatus(false);

		this._storyApiService.save_draft(id, data)
			.then(response => {
				this._updateStatus(true);
				this._hasChanged = false;
			})
			.catch(error => {
				this._updateStatus(true);
			});
	}

	_launchDialog(evt) {
		const modalDialog = this._getModalDialog();
		modalDialog.modal('show');
	}

	_cancel(evt) {
		if (this._hasChanged && !confirm(this._options.messages.beforeUnload)) {
			evt.preventDefault();
			return;
		}

		this._hasChanged = false;
	}

	_getLanguage() {
		if (!this._language) {
			this._language = this._storyContainer.getAttribute('data-language') || 'en';
		}
		return this._language;
	}

	_getStory() {
		const id = this._storyContainer.getAttribute('data-id');

		if (id) {
			return this._storyApiService.getItem(id)
				.then(data => data.story);
		} else {
			return this._storyApiService.last_draft()
				.then(data => data.draft);
		}
	}

	_getModalDialog() {
		if (!this._modalDialog) {
			this._modalDialog = $(`#${this._options.dialogId}`);

			this._modalDialog.modal({
				show: false
			})
		}

		return this._modalDialog;
	}

	_buildStoryChoice(items, story) {
		const options = {
			choices: items || [],
			// addItems: false,
			// removeItems: false,
		};

		const choices = new Choices(this._categorySel, options);

		if (story.category && typeof story.category === 'object') {
			choices.setChoiceByValue(story.category.id);
		}

		if (story.anonymous) {
			this._anonymousCheckbox.checked = true;
		}

		return choices;
	}

	_getCategories() {
		return this._categoryApiService.getItems()
			.then(data => {
				const items = new Array();

				for (const [index, value] of data.items.entries()) {
					items.push({
						id: value.id,
						value: value.id,
						label: value.name
					});
				}

				data.items = items;

				return data;
			});
	}

	_getData() {
		if (!this._bodyEditor || !this._titleEditor || !this._categoryChoice) {
			return null;
		}

		const category_id = this._categoryChoice.getValue(true);

		return Object.assign({}, {
			title: this._getText(this._titleEditor.getData()),
			body: '',
			extra_body: this._bodyEditor.getData(),
			category_id: category_id,
			anonymous: this._anonymousCheckbox.checked ? 1 : 0
		});
	}

	_updateStatus(enabled) {
		if (!!enabled) {
			this._publishBtn.removeAttribute('disabled');
			this._saveDraftBtn.removeAttribute('disabled');

			this._spinnerHelper.stop();
		} else {
			this._publishBtn.setAttribute('disabled', 'disabled');
			this._saveDraftBtn.setAttribute('disabled', 'disabled');

			this._spinnerHelper.start();
		}
	}

	_validate() {
		let isValid = true;

		this._titleEditor.sourceElement.classList.remove('warning-validation');

		if (this._isEmptyEditor(this._titleEditor)) {
			this._titleEditor.sourceElement.classList.add('error-validation');
			isValid = false;
		}

		this._bodyEditor.sourceElement.classList.remove('warning-validation');

		if (this._isEmptyEditor(this._bodyEditor)) {
			this._bodyEditor.sourceElement.classList.add('error-validation');
			isValid = false;
		}

		return isValid;
	}

	_isEmptyEditor(editor) {
		const data = editor.getData();
		const t = this._getText(data);

		if (t && t.trim().length) {
			return false;
		}

		return true;
	}

	_getText(srcHtml) {
		if (!srcHtml) {
			return '';
		}
		let d = document.createElement('div');
		d.innerHTML = srcHtml.trim();

		return d.textContent || d.innerText ||  '';
	}
}
