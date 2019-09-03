'use strict';

import { OEmbedApiService } from 'Assets/main/scripts/api';

export class StoryShowComponent {

	constructor(options) {
		this._moduleId = 'story-show-page';
		this._options = Object.assign({
			oEmbedSelector: 'figure.media oembed',
		}, options || {});
	}

	onLoad() {
		this.start();
	}

	start() {
		const pageContainer = document.getElementById(this._moduleId);

		// check if current page match the id of this module
		if (!pageContainer) {
			return;
		}

		this.initEmbedMedia();
	}

	initEmbedMedia() {
		if (!this._options.oEmbedSelector) {
			return;
		}

		this._oembedApiService = new OEmbedApiService();
		let elements = document.querySelectorAll('oembed[url]');

		if (!elements || !elements.length) {
			return;
		}

		elements.forEach(element => {
			let url = element.attributes.url.value;

			this._oembedApiService.getItem(url)
				.then(data => {
					if (!data.response || data.url !== url) {
						return;
					}

					if (!data.response.html) {
						return;
					}

					let container = document.createElement('div');
					container.innerHTML = data.response.html;
					container = container.childNodes[0];

					container.removeAttribute('height');
					container.removeAttribute('width');

					element.parentNode.replaceChild(container, element);
				});
		});
	}
}
