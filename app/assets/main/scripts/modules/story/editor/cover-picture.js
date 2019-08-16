"use strict";

import { AppConfig } from 'Assets/main/scripts/config';
import { SpinnerHelper } from 'Assets/helpers';
import { PictureApiService } from 'Assets/main/scripts/api';

export class CoverPicturePlugin {

	constructor(options) {
		this._options = Object.assign({
			picture: 0,
			post_id: 0,
			coverPictureSelector: '.cover-picture',
			inputFileSelector: 'cover-picture-upload',
			updatePictureSelector: '.cover-picture-panel span.update, .cover-picture-button',
			removeButtonSelector: '.cover-picture-panel span.delete',
		}, options || {});
		this._init();
	}

	_init() {
		this._coverPicture = document.querySelector(this._options.coverPictureSelector);

		if (!this._coverPicture) {
			return;
		}

		this._pictureApiHelper = new PictureApiService(AppConfig.pictureApiUrl);
		this._fileReader = new FileReader();
		this._inputFile = document.getElementById(this._options.inputFileSelector);
		this._uploadBtn = document.querySelectorAll(this._options.updatePictureSelector);
		this._removeBtn = document.querySelector(this._options.removeButtonSelector);
		this._spinnerHelper = new SpinnerHelper();

		this._setupListeners();
		this._updateCoverPicture();
	}

	_setupListeners() {
		// monitor changes on the file reader
		this._fileReader.addEventListener('load', () => {
			this._updateStatus(false);
			this._upload()
				.then(response => {
					this._updateStatus(true);
					this._options.picture = response.picture;
					this._updateCoverPicture();
				})
				.catch(error => {
					this._updateStatus(true);
				});
		}, false);

		// monitor changes on the input file
		this._inputFile.addEventListener('change', () => {
			this._fileReader.readAsDataURL(this._inputFile.files[0]);
		});

		// trigger the input file to search for a picture
		this._uploadBtn.forEach((btn) => {
			btn.addEventListener('click', (evt) => {
				evt.preventDefault();
				this._inputFile.click();
			});
		});

		// remove picture
		this._removeBtn.addEventListener('click', (evt) => {
			evt.preventDefault();

			this._updateStatus(false);
			this._remove()
				.then(response => {
					this._updateStatus(true);
					this._options.picture = null;
					this._updateCoverPicture();
				})
				.catch(error => {
					this._updateStatus(true);
				});
		});
	}

	_updateCoverPicture() {
		this._coverPicture.style.backgroundImage = '';
		this._coverPicture.classList.remove('has-picture');

		if (!this._options.picture) {
			return;
		}

		const picture = this._options.picture;
		this._coverPicture.style.backgroundImage = `url(${picture.image_url})`;
		this._coverPicture.classList.add('has-picture');
	}

	_upload() {
		const data = {
			'file': this._inputFile.files[0],
			'post_id': this._options.post_id,
		};

		// Starts the upload process.
		return this._pictureApiHelper.upload(data);
	}

	_remove() {
		if (!this._options.picture) {
			return;
		}

		const id = this._options.picture.id;

		return this._pictureApiHelper.delete(id);
	}

	_updateStatus(enabled) {
		if (!!enabled) {
			this._spinnerHelper.stop();
		} else {
			this._spinnerHelper.start();
		}
	}
}

