'use strict';

import { UserApiService, SessionApiService } from 'Assets/main/scripts/api';

export default {
	namespaced: true,
	state: {
		profile: []
	},
	getters: {

	},
	mutations: {
		updateProfile(state, profile) {
			state.profile = profile;
		}
	},
	actions: {
		fetchProfile({ commit }) {
			const userProfileService = new UserApiService();

			return new Promise((resolve, reject) => {
				userProfileService.getProfile().then(data => {
					if (!data.user) {
						reject();
						return;
					}
					commit('updateProfile', data.user);
					resolve();
				});
			});
		},
		logout({ commit, dispatch }) {
			return new Promise((resolve, reject) => {
				const sessionApiService = new SessionApiService();

				sessionApiService.logout().then(data => {
					if (data.message) {
						dispatch('notification/notify', {message: data.message}, {root:true});
					}

					commit('updateProfile', {anonymous:true});
					resolve();
				});
			});
		}
	}
};
