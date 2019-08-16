"use strict";

import Vue from 'vue';

export class TemplateHelper extends Vue {
	constructor(srcOptions) {
		const options = Object.assign({}, {
			delimiters: ['<%', '%>']
		}, srcOptions);

		super(options);
	}
}
