<template>
	<ul class="media-list" v-bind:class="{ 'media-top-nested': depth > 5, 'else': depth <= 5 }">
		<li class="media" v-for="comment in comments" v-bind:key="comment.id">
			<CommentItem :comment="comment"></CommentItem>
			<CommentList v-if="comment.children && comment.children.length"
				:comments="comment.children"
				:depth="depth + 1" />
		</li>
	</ul>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import CommentItem from './comment-item.vue';

export default {
	name: 'CommentList',
	components: {
		CommentItem,
	},
	props: {
		comments: {
			type: Array,
			required: true
		},
		depth: {
			type: Number,
			default: 0
		}
	}
}
</script>
