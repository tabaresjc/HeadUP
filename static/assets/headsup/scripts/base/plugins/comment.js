define(['jquery'], function($) {
	'use strict';

	var targetReplyBtnSel = '.comment-reply',
		targetCancelBtnSel = '.comment-cancel-btn',
		targetTextAreaSel = '.panel-comment textarea, .panel-comment-list textarea';

	// reply comment
	$('body').on('click', targetReplyBtnSel, onReplyClick);

	// cancel comment window
	$('body').on('click', targetCancelBtnSel, onCancelClick);

	// autogrow textarea
	$('body').on('keyup', targetTextAreaSel, textAreaAutoGrow);

	function onReplyClick(e) {
		e.preventDefault();
		var btn = $(this);
		var commentId = btn.attr('data-comment-id');

		$('.reply-wrapper').remove();
		var html = $('#reply-template').html();

		btn.parent().after(html);

		$('.reply-wrapper').find('#comment_id').val(commentId);
	}

	function onCancelClick(e) {
		e.preventDefault();

		var parent = $(this).closest('.reply-wrapper');

		parent.remove();
	}

	function textAreaAutoGrow() {
		var element = this;
		var height = $(this).height();

		element.style.height = '5px';
		element.style.height = (element.scrollHeight) + 'px';
	}
});
