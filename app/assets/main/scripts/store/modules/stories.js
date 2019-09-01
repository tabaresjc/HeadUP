'use strict';

import { StoryApiService } from 'Assets/main/scripts/api';

export default {
	namespaced: true,
	state: {
		page: 1,
		items: [],
		storyApiService: null
	},
	getters: {
		page: (state) => {
			return state.page;
		},
		storyApiService: (state) => {
			if (!state.storyApiService) {
				state.storyApiService = new StoryApiService()
			}
			return state.storyApiService;
		}
	},
	mutations: {
		pushItems(state, items) {
			state.items.push(...items);
		},
		incrementPage(state) {
			state.page++;
		}
	},
	actions: {
		fetchItems({ commit, getters, dispatch }, params) {
			return new Promise((resolve, reject) => {
				getters.storyApiService.getItems(getters.page, params)
					.then(data => {
						if (!data.stories || !data.stories.length) {
							resolve({completed: true});
							return;
						}

						commit('pushItems', data.stories);
						commit('incrementPage');
						resolve({completed: false});
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject();
					});
			});
		},
	}
};
