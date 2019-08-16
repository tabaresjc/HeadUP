"use strict";

import $ from 'jquery';
import io from 'socket.io-client';
import { LocalStorageHelper } from 'Assets/helpers';

export class VoteComponent {

	constructor(options) {
		this._options = Object.assign({
			containerSel: '.story-feed-list',
			voteBtnSel: '.story-social .upvote',
		}, options || {});

		this._localStorageHelper = new LocalStorageHelper();
	}

	onLoad() {
		this.start();
	}

	start() {
		const container = this._pageContainer = document.querySelector(this._options.containerSel);

		if (!container) {
			return;
		}

		// establish connection to server via socket.io
		this._socket = io.connect();
		this._body = $('body');

		// setup event listeners
		this._setupListeners();
		this._retrieveVotes();
	}

	_setupListeners() {
		this._socket.on('vote_results', this._onVoteResults.bind(this));
		this._body.on('click', this._options.voteBtnSel, this._onVoteClick.bind(this));
	}

	_retrieveVotes() {
		this._votes = this._localStorageHelper.get('my_votes');
	}

	_onVoteResults(message) {
		let target_id = message['target_id'];
		let count = message['count'];
		let is_upvote = message['is_upvote'];

		$(`.vote-results[data-id="${target_id}"]`)
			.each(function(index, el) {
				$(el).text(count);
			});

		if (is_upvote) {
			$(`.upvote[data-id="${target_id}"]`).addClass('active');
		} else {
			$(`.upvote[data-id="${target_id}"]`).removeClass('active');
		}
	}

	_onVoteClick(e) {
		e.preventDefault();
		let target = e.target;

		$(target).blur();

		const target_id = parseInt(target.getAttribute('data-id'));
		let payload = { 'target_id': target_id };

		this._socket.emit('vote_post', payload);
	}
}
