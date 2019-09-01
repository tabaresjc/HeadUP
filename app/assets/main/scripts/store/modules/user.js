'use strict';

import { UserApiService, SessionApiService } from 'Assets/main/scripts/api';

export default {
	namespaced: true,
	state: {
		profile: [],
		userApiService: null,
		sessionsApiService: null
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
