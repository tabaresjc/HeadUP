'use strict';

import { AppConfig } from 'Assets/main/scripts/config';
import { UserApiService } from 'Assets/main/scripts/api';

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
			const userProfileService = new UserApiService(AppConfig.userApiUrl);

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
		}
	}
};
