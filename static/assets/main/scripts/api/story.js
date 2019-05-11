"use strict";

import { ApiBase } from 'Assets/main/scripts/lib';

export class StoryApiHelper extends ApiBase {

	constructor(url) {
		super(url);
	}

	getItem(id) {
		const endpoint = `item/${ id }`;

		return this.fetch(endpoint, {}, {
			method: 'GET'
		});
	}


	last_draft() {
		return this.fetch('last-draft', {}, {
			method: 'GET'
		});
	}

	save_draft(id, data) {
		const endpoint = `save-draft/${ id }`;

		return this.fetch(endpoint, data, {
			method: 'POST'
		});
	}

	publish(id, data) {
		const endpoint = `publish/${ id }`;

		return this.fetch(endpoint, data, {
			method: 'POST'
		});
	}
}
