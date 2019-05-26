"use strict";

import { AppConfig } from 'Assets/main/scripts/config';
import { StoryApiHelper } from 'Assets/main/scripts/api';
import $ from 'jquery';
import _ from 'lodash';
import InfiniteScroll from 'infinite-scroll';

export class FeedModule {

	constructor(options) {
		this._moduleId = 'feed-page';
		this._options = Object.assign({
			targetScrollSelector: '.stories-list-container',
			targetItemSelector: '.story-item'
		}, options || {});
	}

	onLoad() {
		this.start();
	}

	start() {
		const pageContainer = this._pageContainer = document.getElementById(this._moduleId);

		// check if current page match the id of this module
		if (!pageContainer) {
			return;
		}

		this._page = 1;
		this._maxPages = 20;
		this._limit = 20;
		this._endScroll = false;
		this._baseUrl = `${AppConfig.storyApiUrl}/items`;
		// this._storyApiHelper = new StoryApiHelper(AppConfig.storyApiUrl);
		this._feedContainer = document.querySelector(this._options.targetScrollSelector);
		this._infiniteScroll = new InfiniteScroll(this._feedContainer, {
			path: () => {
				if (this._endScroll) {
					return false;
				}
				return `${this._baseUrl}/${this._page}?limit=${this._limit}`;
			},
			// load response as flat text
			responseType: 'json',
			status: '.page-load-status',
			history: false,
			checkLastPage: false
		});

		this._setupListeners();

		// load initial page
		this._infiniteScroll.loadNextPage();
	}

	_setupListeners() {
		this._infiniteScroll.on('load', (r) => {
			this._onScrollLoad(r);
		});

		this._infiniteScroll.on('error', (e) => {
			console.error(`[HUP] InfiniteScroll =>`, e);
		});
	}

	_onScrollLoad(response) {
		const data = response.data;

		const templateFn = this._getTemplateFn();
		const resultHtml = templateFn(data);
		const proxyElem = document.createElement('div');
		proxyElem.innerHTML = resultHtml;
		const items = proxyElem.querySelectorAll(this._options.targetItemSelector);
		this._infiniteScroll.appendItems(items);

		const totalPages = Math.floor(1 + (data.total / this._limit));

		if (this._page < this._maxPages && this._page < totalPages) {
			this._page += 1;
		} else {
			this._infiniteScroll.option({
				loadOnScroll: false,
				scrollThreshold: false
			});
			this._infiniteScroll.showStatus('last');
			this._endScroll = true;
		}
	}

	_getTemplateFn() {
		if (!this._templateFn) {
			const targetTemplateSelector = this._feedContainer.getAttribute('data-target-tmpl');
			const targetTemplate = document.getElementById(targetTemplateSelector);
			this._templateFn = _.template(targetTemplate.innerHTML);
		}

		return this._templateFn;
	}
}
