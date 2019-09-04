'use strict';

export class MenuComponent {
	constructor(options) {
		this._elementId = location.hash;
		this._options = Object.assign({
			scrollToTime: 1000
		}, options || {});
	}

	onReady() {
		setTimeout(this.stopScrolling.bind(this));
	}

	onLoad() {
		setTimeout(
			this.scrollToElement.bind(this),
			this._options.scrollToTime
		);
	}

	stopScrolling() {
		if (location.hash) {
			this._elementId = location.hash;
			window.scrollTo(0, 0);
		}
	}

	scrollToElement() {
		if (!this._elementId) {
			return;
		}

		let target = document.querySelector(this._elementId);

		if (!target) {
			return;
		}

		target.scrollIntoView({behavior: 'smooth', block: 'end', inline: 'nearest'});
	}
}
