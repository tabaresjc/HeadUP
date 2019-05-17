"use strict";

import { AppConfig } from 'Assets/main/scripts/config';
import { StoryApiHelper, CategoryApiHelper } from 'Assets/main/scripts/api';
import { SpinnerHelper } from 'Assets/helpers';
import { ImageUploadAdapterPlugin } from './upload';
import Choices from 'choices.js';

export class StoryEditorModule {

	constructor(options) {
		this._moduleId = 'story-editor-page';
		this._options = Object.assign({
			containerId: 'story-container',
			titleId: 'story-title',
			bodyId: 'story-body',
			publishId: 'story-publish',
			saveDraftId: 'story-save-draft',
			categorySelectId: 'story-category'
		}, options || {});
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

		this._storyApiHelper = new StoryApiHelper(AppConfig.storyApiUrl);
		this._categoryApiHelper = new CategoryApiHelper(AppConfig.categoryApiUrl);
		this._spinnerHelper = new SpinnerHelper();

		if (!this._options.titleId || !this._options.bodyId) {
			console.warn(`[HUP] unable to initialize editor`);
			return;
		}

		this._storyContainer = document.getElementById(this._options.containerId);
		this._titleTxt = document.getElementById(this._options.titleId);
		this._bodyTxt = document.getElementById(this._options.bodyId);
		this._categorySel = document.getElementById(this._options.categorySelectId);

		if (!this._storyContainer || !this._titleTxt || !this._bodyTxt) {
			console.warn(`[HUP] editor can't be initialized`);
			return;
		}

		const promises = [
			this.setupTitle(),
			this.setupBody(),
			this.getStory(),
			this.getCategories()
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
				this._bodyEditor.setData(this._story.extra_body || '');
				this._categoryChoice = this.buildStoryChoice(
					this._categoryData.items,
					this._story);

				this.setupListeners();

				console.info(`[HUP] editor initialized`);
				this._spinnerHelper.stop();
			})
			.catch(error => {
				console.error(error.stack);
				this._spinnerHelper.stop();
			});
	}

	setupTitle() {
		const config = {
			placeholder: this._titleTxt.getAttribute('data-placeholder'),
			blockToolbar: [],
			balloonToolbar: [],
			plugins: ['Essentials', 'Paragraph']
		};

		return BalloonEditor.create(this._titleTxt, config);
	}

	setupBody() {
		const config = {
			placeholder: this._bodyTxt.getAttribute('data-placeholder'),
			extraPlugins: [ImageUploadAdapterPlugin],
		};

		return BalloonEditor.create(this._bodyTxt, config);
	}

	setupListeners() {
		this._publishBtn = document.getElementById(this._options.publishId);
		this._publishBtn.addEventListener('click', this.publishStory.bind(this));

		this._saveDraftBtn = document.getElementById(this._options.saveDraftId);
		this._saveDraftBtn.addEventListener('click', this.saveDraft.bind(this));
	}

	publishStory(evt) {
		evt.preventDefault();

		const id = this._story.id;
		const data = this.getData();

		if (!id || !data) {
			return false;
		}

		this.updateStatus(false);

		this._storyApiHelper.publish(id, data)
			.then(response => {
				this.updateStatus(true);

				if (response.redirect_to) {
					window.location = response.redirect_to;
				}
			})
			.catch(error => {
				this.updateStatus(true);
			});
	}

	saveDraft(evt) {
		evt.preventDefault();

		const id = this._story.id;
		const data = this.getData();

		if (!id || !data) {
			return false;
		}

		this.updateStatus(false);

		this._storyApiHelper.save_draft(id, data)
			.then(response => {
				this.updateStatus(true);
			})
			.catch(error => {
				this.updateStatus(true);
			});
	}

	getStory() {
		const id = this._storyContainer.getAttribute('data-id');

		if (id) {
			return this._storyApiHelper.getItem(id)
				.then(data => data.story);
		} else {
			return this._storyApiHelper.last_draft()
				.then(data => data.draft);
		}
	}

	buildStoryChoice(items, story) {
		const options = {
			choices: items || [],
			// addItems: false,
			// removeItems: false,
		};

		const choices = new Choices(this._categorySel, options);

		if (typeof story.category === 'object') {
			choices.setChoiceByValue(story.category.id);
		}

		return choices;
	}

	getCategories() {
		return this._categoryApiHelper.getItems()
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

	getData() {
		if (!this._bodyEditor || !this._titleEditor || !this._categoryChoice) {
			return null;
		}

		const category_id = this._categoryChoice.getValue(true);

		return Object.assign({}, {
			title: this._getText(this._titleEditor.getData()),
			body: '',
			extra_body: this._bodyEditor.getData(),
			category_id: category_id
		});
	}

	updateStatus(enabled) {
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

	_getText(srcHtml) {
		if (!srcHtml) {
			return '';
		}
		let d = document.createElement('div');
		d.innerHTML = srcHtml.trim();

		return d.textContent;
	}
}
