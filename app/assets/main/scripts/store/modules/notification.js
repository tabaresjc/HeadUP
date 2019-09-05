'use strict';

import alertify from 'Lib/alertifyjs/build/alertify.js';

export default {
	namespaced: true,
	state: {
		categories: null
	},
	getters: {
		categories: (state) => {
			if (!state.categories) {
				state.categories = [
					{ id: 'message', value: 'success' },
					{ id: 'success', value: 'success' },
					{ id: 'error', value: 'error' },
					{ id: 'warning', value: 'warning' }
				]
			}
			return state.categories;
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
		notify({ getters }, payload) {
			let categoryName = getters.findCategoryName(payload.category);
			alertify.notify(payload.message, categoryName, payload.waitSeconds || 5);
		},
		log({ dispatch }, payload) {
			// capture errors raised by API
			if (payload.message && typeof payload.message === 'string') {
				dispatch('notify', { message: payload.message, category: 'error' });
			}
		},
		confirm({ dispath }, options) {
			return new Promise((resolve, reject) => {
				if (!options || !options.message) {
					reject('Not enough parameters, [title, message] are required!');
					return;
				}

				alertify.confirm(options.title || 'HeadUP', options.message,
					() => {
						resolve({result: 'ok'});
					},
					() => {
						resolve({result: 'cancel'});
					});
			});
		}
	}
};
