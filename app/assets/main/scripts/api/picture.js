"use strict";

import { ApiBase } from 'Assets/helpers';

export class PictureApiService extends ApiBase {

	constructor(url) {
		super(url);
	}

	getItem(id) {
		const endpoint = `item/${id}`;

		return this.request({
			url: endpoint,
			method: 'GET'
		});
	}

	upload(data, callbacks) {
		const endpoint = `upload`;

		const options = Object.assign({
			url: endpoint,
			method: 'POST',
			data: data,
			onUploadProgress: function (progressEvent) {
				if (callbacks && typeof callbacks.onUploadProgress === 'function') {
					callbacks.onUploadProgress(progressEvent);
				}
			},
			onDownloadProgress: function (progressEvent) {
				if (callbacks && typeof callbacks.onDownloadProgress === 'function') {
					callbacks.onDownloadProgress(progressEvent);
				}
			},
		});

		return this.requestUpload(options);
	}

	delete(id) {
		const endpoint = `delete/${id}`;

		return this.request({
			url: endpoint,
			method: 'POST'
		});
	}
}
