
import $ from 'jquery';

const targetReplyBtnSel = '.comment-reply';
const targetCancelBtnSel = '.comment-cancel-btn';
const targetTextAreaSel = '.panel-comment textarea, .panel-comment-list textarea';
const commentContainerSel = '.reply-wrapper';
const bodyElement = $('body');

bodyElement
	// reply comment
	.on('click', targetReplyBtnSel, onReplyClick)
	// cancel comment window
	.on('click', targetCancelBtnSel, onCancelClick)
	// autogrow textarea
	.on('keyup', targetTextAreaSel, textAreaAutoGrow);

function onReplyClick(e) {
	e.preventDefault();
	var btn = $(this);
	var commentId = btn.attr('data-comment-id');

	$(commentContainerSel).remove();
	var html = $('#reply-template').html();

	btn.parent().after(html);

	$(commentContainerSel).find('#comment_id').val(commentId);
}

function onCancelClick(e) {
	e.preventDefault();

	var parent = $(this).closest(commentContainerSel);

	parent.remove();
}

function textAreaAutoGrow() {
	var element = this;
	var height = $(this).height();

	element.style.height = '5px';
	element.style.height = (element.scrollHeight) + 'px';
}
