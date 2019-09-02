'use strict';

import { AppConfig } from 'Assets/main/scripts/appConfig';
import $ from 'jquery';

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

		if (!this._options.oEmbedSelector) {
			console.warn(`[HUP] unable to initialize page`);
			return;
		}

		this.initEmbedMedia();
	}

	initEmbedMedia() {
		if(!iframely) {
			console.warn(`[HUP] unable to find "iframely"`);
		}

		let elements = document.querySelectorAll('oembed[url]');

		if (!elements || !elements.length) {
			return;
		}

		elements.forEach(element => {
			iframely.load(element, element.attributes.url.value);
		});
	}
}
