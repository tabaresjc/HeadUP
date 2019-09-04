'use strict';

import { UserApiService, SessionApiService } from 'Assets/main/scripts/api';

export default {
	namespaced: true,
	state: {
		profile: [],
		votes: [],
		userApiService: null,
		sessionsApiService: null,
		localStorage: null,
	},
	getters: {
		userApiService: (state) => {
			if (!state.userApiService) {
				state.userApiService = new UserApiService()
			}
			return state.userApiService;
		},
		sessionsApiService: (state) => {
			if (!state.sessionsApiService) {
				state.sessionsApiService = new SessionApiService()
			}
			return state.sessionsApiService;
		}
	},
	mutations: {
		updateProfile(state, profile) {
			state.profile = profile;
		},
		setVotes(state, votes) {
			state.votes = votes;
		},
		refreshVote(state, payload) {
			if (payload.is_upvote) {
				state.votes.push(payload.target_id);
				return;
			}

			let index = state.votes.indexOf(payload.target_id);

			if (index < 0) {
				return;
			}

			state.votes.splice(index, 1);
		}
	},
	actions: {
		fetchProfile({ commit, getters, dispatch }) {
			return new Promise((resolve, reject) => {
				getters.userApiService.getProfile()
					.then(data => {
						if (!data.user) {
							reject();
							return;
						}
						commit('updateProfile', data.user);
						if (data.user.is_authenticated) {
							dispatch('fetchStoriesVotes');
						}
						resolve();
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject();
					});
			});
		},
		fetchStoriesVotes({ commit, getters, dispatch }) {
			return new Promise((resolve, reject) => {
				getters.userApiService.getStoriesVotes()
					.then(data => {
						let votes = data.votes || [];
						commit('setVotes', votes);
						resolve();
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject();
					});
			});
		},
		logout({ commit, getters, dispatch }) {
			return new Promise((resolve, reject) => {
				getters.sessionsApiService.logout()
					.then(data => {
						if (data.message) {
							dispatch('notification/notify', { message: data.message }, { root: true });
						}

						commit('updateProfile', { anonymous: true });
						resolve();
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject();
					});
			});
		}
	}
};
