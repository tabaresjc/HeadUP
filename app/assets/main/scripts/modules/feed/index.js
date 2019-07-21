"use strict";

import { AppConfig } from 'Assets/main/scripts/config';
import $ from 'jquery';
import _ from 'lodash';
import InfiniteScroll from 'infinite-scroll';
import { GetLanguage } from 'Assets/helpers';

export class FeedModule {

	constructor(options) {
		this._moduleId = 'feed-page';
		this._options = Object.assign({
			targetScrollSelector: '.story-feed-list',
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
		this._feedContainer = document.querySelector(this._options.targetScrollSelector);
		this._infiniteScroll = new InfiniteScroll(this._feedContainer, {
			path: () => {
				if (this._endScroll) {
					return false;
				}

				let url = `${this._baseUrl}/${this._page}`;
				let params = this._getParams();

				return `${url}?${params}`;
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
			let response = r;

			// ie fix
			if (typeof response === 'string') {
				response = JSON.parse(response);
			}

			this._onScrollLoad(response);
		});

		this._infiniteScroll.on('error', (e) => {
			console.error(`[HUP] InfiniteScroll =>`, e);
		});
	}

	_onScrollLoad(response) {
		const data = response.data;

		const templateFn = this._getTemplateFn();
		const items = this._wrapHtml(templateFn(data))
			.querySelectorAll(this._options.targetItemSelector);

		this._infiniteScroll.appendItems(items);

		const totalPages = Math.floor(1 + (data.total / this._getLimit()));

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

	_getParams() {
		return [
			`category=${this._getCategory()}`,
			`limit=${this._getLimit()}`,
			`lang=${this._getLanguage()}`
		].join('&');
	}

	_getLimit() {
		if (!this._limit) {
			this._limit = this._feedContainer.getAttribute('data-target-limit') || 20;
		}
		return this._limit;
	}

	_getCategory() {
		if (!this._category) {
			this._category = this._feedContainer.getAttribute('data-target-category') || '';
		}
		return this._category;
	}

	_getLanguage() {
		if (!this._language) {
			this._language = this._feedContainer.getAttribute('data-target-lang') || GetLanguage();
		}
		return this._language;
	}

	_wrapHtml(str) {
		const div = document.createElement('div');
		div.innerHTML = str;
		return div;
	}
}
