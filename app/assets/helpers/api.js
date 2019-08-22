"use strict";

import axios from 'axios';

export class ApiBase {

	constructor(baseUrl) {
		this.baseUrl = baseUrl;
		this.init();
	}

	init() {
		// setup csrf for every request made to the api
		axios.defaults.headers.common['X-CSRFToken'] = this._getToken();
	}

	request(options) {
		if (!options.url) {
			console.warn(`[HeadUP] ApiBase found no url`);
		}

		const httpHandler = this._createHttpClient();

		const config = Object.assign({
			method: 'GET',
			params: {},
			data: {}
		}, options);

		return httpHandler.request(config)
			.then(response => this._transformResponse(response));
	}

	requestUpload(options) {
		if (!options.url) {
			console.warn(`[HeadUP] ApiBase found no url`);
		}

		const httpHandler = this._createHttpClient({
			headers: {
				'Content-Type': 'multipart/form-data'
			}
		});

		const data = this._buildData(data);

		const config = Object.assign({
			method: 'POST',
		}, options, { data: data });

		return httpHandler.request(config)
			.then(response => this._transformResponse(response));
	}

	_createHttpClient(options) {
		const config = Object.assign({
			baseURL: this.baseUrl,
			withCredentials: false,
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			responseType: 'json'
		}, options || {});

		return axios.create(config);
	}

	_transformResponse(response) {
		if (typeof response === 'string') {
			try {
				response = JSON.parse(response);
			} catch (e) {
			}
		}

		if (response.data && response.data.data) {
			return response.data.data;
		}

		if (response.data) {
			return response.data;
		}

		return response;
	}

	_getHandler(endpoint, options) {
		const xhr = new XMLHttpRequest();
		const url = this._getUrl(endpoint, options);

		xhr.open(options.method, url, true);
		xhr.responseType = 'json';

		return xhr;
	}

	_buildData(srcData) {
		// prepare form data.
		const data = new FormData();

		for (const [k, v] of Object.entries(srcData)) {
			data.append(k, v);
		}

		return data;
	}

	_getToken() {
		const paramName = 'csrf-token';
		const q = document.querySelectorAll(`meta[name="${paramName}"]`);

		if (!q || !q.length) {
			return '';
		}

		const n = q[0];

		return n.getAttribute('content');
	}
}
