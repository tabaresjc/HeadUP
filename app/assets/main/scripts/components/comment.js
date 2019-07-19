"use strict";

import $ from 'jquery';

export class CommentComponent {
	constructor() {
		this._panelComment = '.panel-comment';
		this._targetReplyBtnSel = '.comment-reply';
		this._targetCancelBtnSel = '.comment-cancel-btn';
		this._targetTextAreaSel = '.panel-comment textarea, .panel-comment-list textarea';
		this._commentContainerSel = '.reply-wrapper';
		this._replyTemplate = '#reply-template';
	}

	onLoad() {
		if (!this._panelComment.length) {
			return;
		}

		const bodyEl = $('body');

		bodyEl
			// reply comment
			.on('click', this._targetReplyBtnSel, (evt) => {
				this.onReplyClick(evt);
			})
			// cancel comment window
			.on('click', this._targetCancelBtnSel, (evt) => {
				this.onCancelClick(evt);
			})
			// autogrow textarea
			.on('keyup', this._targetTextAreaSel, (evt) => {
				this.textAreaAutoGrow(evt);
			});
	}

	onReplyClick(evt) {
		evt.preventDefault();
		console.log('onReplyClick')
		let btn = $(evt.currentTarget);
		let commentId = btn.attr('data-comment-id');

		$(this._commentContainerSel).remove();
		let html = $(this._replyTemplate).html();

		btn.parent().after(html);

		$(this._commentContainerSel).find('#comment_id').val(commentId);
	}

	onCancelClick(evt) {
		evt.preventDefault();
		let btn = $(evt.currentTarget);
		let parent = btn.closest(this._commentContainerSel);
		parent.remove();
	}

	textAreaAutoGrow(evt) {
		let element = evt.currentTarget;
		element.style.height = '5px';
		element.style.height = (element.scrollHeight) + 'px';
	}
}
