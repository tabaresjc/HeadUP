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
		let elements = document.querySelectorAll('.story-body oembed[url]');

		if (!elements || !elements.length) {
			return;
		}

		elements.forEach((element, index) => {
			let url = element.attributes.url.value;
			let newId = `oembed-media-${index}`;
			element.setAttribute('id', newId);

			this._oembedApiService.getItem(url)
				.then(data => {
					if (!data.response || data.url !== url) {
						return;
					}

					if (!data.response.html) {
						return;
					}

					setTimeout(() => {
						this.replaceElement(newId, data.response.html);
					});
				});
		});
	}

	replaceElement(id, htmlString) {
		let o = document.getElementById(id);
		if (o.outerHTML) {
			o.outerHTML = htmlString;
		} else {
			let to = document.createElement('div');
			let p = o.parentNode;
			to.innerHTML = '<!--HTML_TO_BE_REPLACED-->';
			p.replaceChild(to, o);
			p.innerHTML = p.innerHTML.replace('<div><!--HTML_TO_BE_REPLACED--></div>', htmlString);
		}
	}
}
