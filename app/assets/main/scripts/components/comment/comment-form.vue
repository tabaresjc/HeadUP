<template>
	<div id="comment-panel" class="row push-down-20">
		<div class="col-md-12 col-sm-12 col-xs-12">
			<div class="panel panel-default panel-comment">
				<div class="panel-body">
					<div class="form-group">
						<textarea class="form-control"
							name="text"
							v-model="commentMessage"
							:placeholder="$t('COMMENT_TEXT_PLACEHOLDER')">
						</textarea>
					</div>
					<div class="actions clearfix">
						<button type="button"
							class="btn btn-primary btn-primary--transparent btn-lg pull-right"
							v-on:click="addComment()"
							v-bind:disabled="!haveContent">
							{{ $t('COMMENT_SUBMIT_BTN') }}
						</button>
					</div>
				</div>
				<div class="login-required" v-if="!user.is_authenticated">
					<div class="column">
						<a :href="endpoints.login" rel="nofollow" class="btn btn-primary">
							{{ $t('LOGIN_BTN') }}
						</a>
						<a :href="endpoints.register" rel="nofollow" class="btn btn-primary">
							{{ $t('REGISTER_BTN') }}
						</a>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
	name: 'CommentForm',
	props: {
		postId: {
			type: Number,
			required: true
		},
		endpoints: {
			type: Object,
			required: true
		}
	},
	data() {
		return {
			commentMessage: ''
		}
	},
	computed: {
		...mapState({
			user: state => state.user.profile
		}),
		commentHtmlId() {
			return `comment-form`;
		},
		haveContent() {
			return this.commentMessage && this.commentMessage.trim().length;
		}
    },
	methods: {
		...mapActions({
			confirm: 'notification/confirm',
			notify: 'notification/notify',
			createComment: 'comments/create'
		}),
		addComment() {
			const data = {
				text: this.commentMessage,
				post_id: this.postId
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

					this.jumpToComment(comment.id);
				});
		},
		jumpToComment(commentId) {
			const elId = `comment-${commentId}`;

			const targetElement = document.getElementById(elId);

			if (!targetElement) {
				return;
			}

			const yCoordinate = targetElement.getBoundingClientRect().top + window.pageYOffset;
			const yOffset = -10;

			window.scrollTo({
				top: yCoordinate + yOffset,
				behavior: 'smooth'
			});
		}
	}
}
</script>
