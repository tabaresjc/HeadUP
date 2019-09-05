'use strict';

import { ApiBase } from 'Assets/helpers';
import { AppConfig } from 'Assets/main/scripts/appConfig';

export class CommentApiService extends ApiBase {

	constructor(url) {
		super(url || AppConfig.commentApiUrl);
	}

	getCommentsByPost(postId) {
		const endpoint = `post/${postId}/items`;

		return this.request({
			url: endpoint,
			method: 'GET'
		});
	}

	create(data) {
		const endpoint = '/';

		return this.request({
			url: endpoint,
			method: 'POST',
			data: data
		});
	}

	update(id, data) {
		const endpoint = `/${id}`;

		return this.request({
			url: endpoint,
			method: 'PUT',
			data: data
		});
	}

	delete(id) {
		const endpoint = `/${id}`;

		return this.request({
			url: endpoint,
			method: 'DELETE'
		});
	}
}
