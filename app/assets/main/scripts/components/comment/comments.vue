<template>
	<div class="row push-down-20" v-if="loaded && comments.length">
		<div class="col-md-12 col-sm-12 col-xs-12">
			<div class="panel panel-comment-list">
				<div class="panel-body">
					<CommentList :comments="comments" />
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import CommentList from './comment-list.vue';

export default {
	name: 'Comments',
	components: {
		CommentList,
	},
	props: {
		postId: {
			type: Number,
			required: true
		}
	},
	data() {
		return {
			loaded: false
		}
	},
	computed: {
		...mapState({
			comments: state => state.comments.items
		})
    },
	methods: {
		...mapActions({
			fetchCommentsByPost: 'comments/fetchCommentsByPost'
		}),
	},
	created() {
		this.loaded = false;

		this.fetchCommentsByPost(this.postId)
			.then(() => {
				this.loaded = true;
			});
	}
}
</script>
