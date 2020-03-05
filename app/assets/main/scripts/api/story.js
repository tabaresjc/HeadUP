'use strict';

import { ApiBase } from 'Assets/helpers';
import { AppConfig } from 'Assets/main/scripts/appConfig';

export class StoryApiService extends ApiBase {

	constructor(url) {
		super(url || AppConfig.storyApiUrl);
	}

	getItems(page, params) {
		const endpoint = '';
		params = {...params, page: page};

		return this.request({
			url: endpoint,
			method: 'GET',
			params: params
		});
	}

	getItem(id) {
		const endpoint = `/${ id }`;

		return this.request({
			url: endpoint,
			method: 'GET'
		});
	}

	deleteItem(id) {
		const endpoint = `/${ id }`;

		return this.request({
			url: endpoint,
			method: 'DELETE'
		});
	}

	hideItem(id) {
		const endpoint = `${id}/hide`;

		return this.request({
			url: endpoint,
			method: 'POST'
		});
	}

	last_draft() {
		const endpoint = 'last-draft';

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
