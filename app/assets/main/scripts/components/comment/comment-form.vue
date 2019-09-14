<template>
	<div id="comment-panel" class="row push-down-20" v-if="user">
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
						<a href="#user-session-modal" data-toggle="modal" rel="nofollow" class="btn btn-primary">
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
import { UtilHelper } from 'Assets/helpers';

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
			loaded: false,
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

					const elId = `comment-${comment.id}`;
					UtilHelper.smootScroll(elId);
				});
		}
	},
	created() {
		let targetElementId = (location.hash || '').replace('#', '');

		if (targetElementId !== 'comment-panel') {
			return;
		}

		window.scrollTo(0, 0);

		let count = 0

		function detectChange() {
			if (count > 4) {
				return;
			}

			let el = document.getElementById(targetElementId);

			if (!el) {
				count++;
				setTimeout(detectChange, 250);
			}

			UtilHelper.smootScroll(targetElementId);
		}

		detectChange();
	}
}
</script>
