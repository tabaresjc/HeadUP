'use strict';

import { AppConfig } from 'Assets/main/scripts/config';
import { PictureApiService } from 'Assets/main/scripts/api';

export class ImageUploadAdapter {

	constructor(loader) {
		// The file loader instance to use during the upload.
		this.loader = loader;
		this._pictureApiHelper = new PictureApiService(AppConfig.pictureApiUrl);
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

				return this._pictureApiHelper.upload(data, {
					onUploadProgress: onProgress
				})
				.then(response => {
					// transforms the response provided by the api, into a format required
					// by the editor
					const picture = response.picture;
					return Object.assign({}, {
						default: picture.image_url
					});
				});
			});
	}

}

export function ImageUploadAdapterPlugin(editor) {
	editor.plugins.get('FileRepository').createUploadAdapter = (loader) => {
		return new ImageUploadAdapter(loader);
	};
}
