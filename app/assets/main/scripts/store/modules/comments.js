'use strict';

import { CommentApiService } from 'Assets/main/scripts/api';

export default {
	namespaced: true,
	state: {
		items: [],
		itemsById: {},
		commentApiService: null
	},
	getters: {
		commentApiService: (state) => {
			if (!state.commentApiService) {
				state.commentApiService = new CommentApiService()
			}
			return state.commentApiService;
		}
	},
	mutations: {
		pushItems(state, items) {
			state.items = items || [];
			state.itemsById = {};
			state.items.forEach((comment) => {
				traverseComments(comment);
			});

			function traverseComments(comment) {
				state.itemsById[comment.id] = comment;

				comment.children.forEach((c) => {
					c.parent = comment;
					traverseComments(c);
				});
			}
		},
		addItem(state, comment) {
			const parentComment = comment.comment_id ? state.itemsById[comment.comment_id] : null;
			if (parentComment) {
				// append to children of parent comment
				if (!parentComment.children) {
					parentComment.children = [];
				}
				parentComment.children.push(comment);
			} else {
				// append to root
				state.items.push(comment);
			}

			state.itemsById[comment.id] = comment;
		},
		deleteItem(state, id) {
			const comment = state.itemsById[id];

			if (!comment) {
				return;
			}

			const parentComment = comment.comment_id ? state.itemsById[comment.comment_id] : null;
			let arr;

			if (parentComment) {
				arr = parentComment.children;
			} else {
				arr = state.items;
			}

			for (let index = 0; index < arr.length; index++) {
				let c = arr[index];
				if (c.id === id) {
					arr.splice(index, 1);
				}
			}

			delete state.itemsById[id];
		}
	},
	actions: {
		fetchCommentsByPost({ commit, getters, dispatch }, postId) {
			return new Promise((resolve, reject) => {
				getters.commentApiService.getCommentsByPost(postId)
					.then(data => {
						commit('pushItems', data.comments);
						resolve();
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject();
					});
			});
		},
		create({ commit, getters, dispatch }, data) {
			return new Promise((resolve, reject) => {
				getters.commentApiService.create(data)
					.then(data => {
						commit('addItem', data.comment);
						resolve(data.comment);
					})
					.catch(err => {
						dispatch('notification/log', err, { root: true });
						reject();
					});
			});
		},
		delete({ commit, getters, dispatch }, id) {
			return new Promise((resolve, reject) => {
				getters.commentApiService.delete(id)
					.then(() => {
						commit('deleteItem', id);
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
