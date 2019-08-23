'use strict';

import alertify from 'Lib/alertifyjs/build/alertify.js';

export default {
	namespaced: true,
	getters: {
		categories() {
			return [
				{ id: 'message', value: 'success' },
				{ id: 'success', value: 'success' },
				{ id: 'error', value: 'error' },
				{ id: 'warning', value: 'warning' }
			];
		},
		findCategoryName: (state, getters) => (id) => {
			let category = getters.categories.find(cat => cat.id === id);

			if (!category) {
				return 'success';
			}

			return category.value;
		}
	},
	actions: {
		notify({ commit, getters }, payload) {
			let categoryName = getters.findCategoryName(payload.category);
			alertify.notify(payload.message, categoryName, payload.waitSeconds || 5);
		}
	}
};
