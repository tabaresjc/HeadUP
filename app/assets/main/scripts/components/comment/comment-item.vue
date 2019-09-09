<template>
	<div :id="commentHtmlId">
		<div class="media-left">
			<a href="javascript:;">
				<img class="media-object"
					:src="comment.profile.profile_picture_url || '/static/images/user.png'"
					:alt="comment.profile.nickname"
					width="64" height="64">
			</a>
		</div>
		<div class="media-body">
			<span class="author"><strong>{{ comment.profile.nickname }}</strong></span>
			<span class="date text-muted">{{ comment.created_at | moment('llll') }}</span>
			<div class="comment-container">
				<div class="text">{{ comment.text }}</div>
			</div>
			<div class="media-footer clearfix" v-if="isAuthenticated">
				<button type="button" class="btn btn-link pull-left"
					v-on:click="deleteComment()"
					v-if="canEdit(comment.profile.id)">
					<i class="glyphicon glyphicon-trash"></i>
				</button>
				<button type="button" class="btn btn-link pull-right"
					v-on:click="toggleReply()"
					v-if="!hasReply">
					{{ $t('COMMENT_REPLY_LBL') }}
				</button>
			</div>
			<div class="reply-wrapper" v-show="hasReply">
				<div class="panel-reply">
					<div class="form-group">
						<textarea class="form-control"
							name="text"
							rows="1"
							v-model="commentMessage"
							:id="commentReplyId"
							:placeholder="$t('COMMENT_REPLY_TEXT_PLACEHOLDER')">
						</textarea>
					</div>
					<div class="actions clearfix">
						<button type="submit" class="btn btn-danger btn-danger--transparent btn-lg pull-left"
							v-on:click="toggleReply()">
							{{ $t('COMMENT_REPLY_CANCEL_BTN') }}
						</button>
						<button type="submit" class="btn btn-primary btn-primary--transparent btn-lg pull-right"
							v-on:click="addComment()"
							v-bind:disabled="!haveContent">
							{{ $t('COMMENT_REPLY_SUBMIT_BTN') }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
	name: 'CommentItem',
	props: {
		comment: {
			type: Object,
			required: true
		}
	},
	data() {
		return {
			hasReply: false,
			replyEventMounted: false,
			commentMessage: ''
		}
	},
	computed: {
		...mapState({
			user: state => state.user.profile
		}),
		commentHtmlId() {
			return `comment-${this.comment.id}`;
		},
		commentReplyId() {
			return `comment-reply-${this.comment.id}`;
		},
		haveContent() {
			return this.commentMessage && this.commentMessage.trim().length;
		},
		isAuthenticated() {
			return this.user.is_authenticated;
		}
    },
	methods: {
		...mapActions({
			confirm: 'notification/confirm',
			notify: 'notification/notify',
			createComment: 'comments/create',
			removeComment: 'comments/delete'
		}),
		canEdit(userId) {
			if(!this.user || !this.user.is_authenticated) {
				return false;
			}

			return this.user.id === userId;
		},
		addComment() {
			if (!this.comment.children) {
				this.comment.children = [];
			}

			const data = {
				text: this.commentMessage,
				comment_id: this.comment.id,
				post_id: this.comment.post_id
			};

			this.createComment(data)
				.then(comment => {
					let message = this.$t('COMMENT_SAVE_SUCESS');

					this.commentMessage = '';
					this.hasReply = false;

					this.notify({
						message: message,
						type: 'success'
					});
				});
		},
		deleteComment() {
			let confirmMessge = this.$t('COMMENT_DELETE_CONFIRMATION', {
				text:this.comment.text.hu_substring(100).hu_nl2br()
			});

			this.confirm({message: confirmMessge})
				.then((response) => {
					if (response.result !== 'ok') {
						return;
					}

					let commentId = this.comment.id;
					let successMessage = this.$t('COMMENT_DELETE_SUCCESS');

					this.removeComment(commentId)
						.then(() => {
							this.notify({
								message: successMessage,
								type: 'success'
							});
						});
				});
		},
		toggleReply() {
			this.hasReply = !this.hasReply;

			if (!this.replyEventMounted) {
				document.getElementById(this.commentReplyId).addEventListener('keydown', ()=> {
					this.fixToHeight(this.commentReplyId, 250);
				});

				this.replyEventMounted = true;
			}
		},
		fixToHeight(id, maxHeight) {
			var text = id && id.style ? id : document.getElementById(id);

			if (!text) {
				return;
			}

			var adjustedHeight = text.clientHeight;

			if (!maxHeight || maxHeight > adjustedHeight) {
				adjustedHeight = Math.max(text.scrollHeight, adjustedHeight);

				if (maxHeight) {
					adjustedHeight = Math.min(maxHeight, adjustedHeight);
				}

				if (adjustedHeight > text.clientHeight) {
					text.style.height = `${adjustedHeight}px`;
				}
			}
		}
	}
}
</script>
