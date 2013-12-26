{% from "shared/_bootstrap_forms.html" import render_inline_field %}
line = '';
line += '<div id="reply_{{comment.id}}" class="well" >';
line += '	<p>Reply to @{{ comment.user.name }}</p>';
line += '	<form action="{{url_for("reply_comment",id=comment.id)}}" method="post" name="ReplyComment" autocomplete="off">';
line += '		{{form.hidden_tag()}}';
line += '		<div class="form-group"><textarea id="text_reply" name="body" placeholder="Your thoughts..." rows="5"></textarea></div>';
line += '		<div class="buttons clearfix">';
line += '			<button id="btn_cancel" type="reset" class="btn btn-lg btn-tales-two">Cancel</button>';
line += '			<button type="submit" class="btn btn-lg btn-tales-one pull-right">Submit</button>';
line += '		</div>';
line += '	</form>';
line += '</div>';
$("#comment_{{comment.id}} .reply").html(line);
$('#reply_{{comment.id}} #text_reply').ckeditor();
$('#reply_{{comment.id}} #btn_cancel').click(function(){
	$("#comment_{{comment.id}} .reply").html('');
	return false;
});
