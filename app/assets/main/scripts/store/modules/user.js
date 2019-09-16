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
		},
		clearVotes(state) {
			state.votes = [];
		}
	},
	actions: {
		fetchProfile({ commit, getters, dispatch }) {
			return new Promise((resolve, reject) => {
				getters.userApiService.getProfile()
					.then(response => {
						if (!response.user) {
							reject();
							return;
						}
						commit('updateProfile', response.user);
						if (response.user.is_authenticated) {
							dispatch('fetchStoriesVotes');
						}
						resolve();
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject(err.response);
					});
			});
		},
		fetchStoriesVotes({ commit, getters, dispatch }) {
			return new Promise((resolve, reject) => {
				getters.userApiService.getStoriesVotes()
					.then(response => {
						let votes = response.votes || [];
						commit('setVotes', votes);
						resolve();
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject(err.response);
					});
			});
		},
		login({ getters, dispatch }, data) {
			return new Promise((resolve, reject) => {
				getters.sessionsApiService.login(data)
					.then((response) => {
						dispatch('fetchProfile');
						resolve(response.user);
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject(err.response);
					});
			});
		},
		logout({ commit, getters, dispatch }) {
			return new Promise((resolve, reject) => {
				getters.sessionsApiService.logout()
					.then(response => {
						if (response.message) {
							dispatch('notification/notify', { message: response.message }, { root: true });
						}

						commit('updateProfile', { anonymous: true });
						commit('clearVotes');
						resolve();
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject(err.response);
					});
			});
		}
	}
};
