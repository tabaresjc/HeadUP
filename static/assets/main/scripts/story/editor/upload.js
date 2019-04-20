"use strict";

import { AppConfig } from 'Assets/main/scripts/config';
import { ApiBase } from 'Assets/main/scripts/lib';

export class ImageUploadAdapter extends ApiBase {

	constructor(url, loader) {
		super(url);
		// The file loader instance to use during the upload.
		this.loader = loader;
	}

	// Starts the upload process.
	upload() {
		const loader = this.loader;

		// handle the results of the upload progress process
		let onProgress = evt => {
			loader.uploadTotal = evt.total;
			loader.uploaded = evt.loaded;
		};

		return this.loader.file
			.then(file => {
				const data = {
					'file': file
				};

				return this.fetch('upload', data, {
					method: 'POST',
					onProgress: onProgress
				})
				.then(response => {
					// transforms the response provided by the api, into a format required
					// by the editor
					return Object.assign({}, {
						default: response.url
					});
				});
			});
	}

}

export function ImageUploadAdapterPlugin(editor) {
	editor.plugins.get('FileRepository').createUploadAdapter = (loader) => {
		return new ImageUploadAdapter(AppConfig.pictureApiUrl, loader);
	};
}
