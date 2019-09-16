'use strict';

import Vue from 'vue';
import { MomentInstance } from 'Assets/helpers';

Vue.directive('date-transform', {
	bind: function (el, binding) {
		let m = MomentInstance();
		let value = binding.value;

		if (!value) {
			return;
		}

		let datetime = value.isUnix ? value.datetime * 1000 : value.datetime;
		el.innerHTML = m(datetime).format(value.format || 'll');
	}
});
