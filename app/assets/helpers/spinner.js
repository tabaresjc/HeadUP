'use strict';

export class SpinnerHelper {
	constructor() {
		this._init();
	}

	_init() {
		this._container = document.getElementById('spinner');

		if (!this._container) {
			this._container = document.createElement('div');
			this._container.setAttribute('id', 'overlay-container');
			this._container.innerHTML = `
			<div class="sk-circle">
				<div class="sk-circle1 sk-child"></div>
				<div class="sk-circle2 sk-child"></div>
				<div class="sk-circle3 sk-child"></div>
				<div class="sk-circle4 sk-child"></div>
				<div class="sk-circle5 sk-child"></div>
				<div class="sk-circle6 sk-child"></div>
				<div class="sk-circle7 sk-child"></div>
				<div class="sk-circle8 sk-child"></div>
				<div class="sk-circle9 sk-child"></div>
				<div class="sk-circle10 sk-child"></div>
				<div class="sk-circle11 sk-child"></div>
				<div class="sk-circle12 sk-child"></div>
			</div>`;
			document.body.appendChild(this._container);
		}
	}

	start() {
		this._container.classList.add('loading');
	}

	stop(timeOut) {
		setTimeout(() => {
			this._container.classList.remove('loading');
		}, timeOut || 250);
	}
}
