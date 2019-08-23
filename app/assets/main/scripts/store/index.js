import Vuex from 'vuex';
import Vue from 'vue';
import state from './state';
import getters from './getters';
import actions from './actions';
import mutations from './mutations';
import user from './modules/user';
import notification from './modules/notification';

Vue.use(Vuex);

export default new Vuex.Store({
	modules: {
		notification,
		user
	},

	state: state,
	getters: getters,
	actions: actions,
	mutations: mutations
});








