define(['jquery'], function($) {
	'use strict';

	$(function() {
		$('body').on('click', '.comment-reply', onReplyClick);
		$('body').on('click', '.comment-cancel-btn', onCancelClick);

		$('.container').on('keyup', '.panel-comment textarea, .panel-comment-list textarea', textAreaAutoGrow);

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
			element.style.height = "5px";
			element.style.height = (element.scrollHeight)+"px";
		}
	});
});
