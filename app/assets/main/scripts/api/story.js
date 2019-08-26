"use strict";

import { ApiBase } from 'Assets/helpers';
import { AppConfig } from 'Assets/main/scripts/config';

export class StoryApiService extends ApiBase {

	constructor(url) {
		super(url || AppConfig.storyApiUrl);
	}

	getItems(page, params) {
		const endpoint = `items/${page}`;

		return this.request({
			url: endpoint,
			method: 'GET',
			params: params
		});
	}

	getItem(id) {
		const endpoint = `item/${ id }`;

		return this.request({
			url: endpoint,
			method: 'GET'
		});
	}

	last_draft() {
		const endpoint = `last-draft`;

		return this.request({
			url: endpoint,
			method: 'GET'
		});
	}

	save_draft(id, data) {
		const endpoint = `save-draft/${ id }`;

		return this.request({
			url: endpoint,
			method: 'POST',
			data: data
		});
	}

	publish(id, data) {
		const endpoint = `publish/${ id }`;

		return this.request({
			url: endpoint,
			method: 'POST',
			data: data
		});
	}
}
