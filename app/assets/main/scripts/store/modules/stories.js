'use strict';

import { StoryApiService } from 'Assets/main/scripts/api';
import $socket from 'Assets/main/scripts/config/socket';

export default {
	namespaced: true,
	state: {
		page: 1,
		items: [],
		itemsById: {},
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
			items.forEach(item => {
				const index = state.items.length;
				state.itemsById[item.id] = index;
				state.items.push(item);
			});
		},
		incrementPage(state) {
			state.page++;
		},
		updateVoteCount(state, payload) {
			const index = state.itemsById[payload.target_id];
			if (isNaN(index) || !state.items || state.items.length < index) {
				return;
			}
			state.items[index].likes = payload.count;
		}
	},
	actions: {
		fetchItems({ commit, getters, dispatch }, params) {
			return new Promise((resolve, reject) => {
				getters.storyApiService.getItems(getters.page, params)
					.then(data => {
						if (!data.total || !data.stories || !data.stories.length) {
							resolve({ completed: true });
							return;
						}

						commit('pushItems', data.stories);
						commit('incrementPage');
						resolve({ completed: false });
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject();
					});
			});
		},
		vote(_, targetId) {
			$socket.emit('vote_story', {
				target_id: targetId
			});
		},
		socket_voteStoryResults({ commit }, payload) {
			if (!payload.target_id) {
				return;
			}

			commit('updateVoteCount', payload);
		}
	}
};
