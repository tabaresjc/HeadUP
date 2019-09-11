<template>
	<div id="user-session-modal" class="modal fade">
		<div class="modal-dialog modal-login">
			<div class="modal-content">
				<div class="modal-header">
					<div class="avatar">
						<img src="/static/images/avatar.png" alt="Avatar">
					</div>
					<h4 class="modal-title">{{ $t('LOGIN_TITLE') }}</h4>
					<button id="user-session-modal-dismiss" type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
				</div>
				<div class="modal-body">
					<div class="form">
						<div class="form-group">
							<input type="text" class="form-control"
								name="email"
								v-model="loginEmail"
								:placeholder="$t('MAIL_LBL')"
								required="required">
						</div>
						<div class="form-group">
							<input type="password" class="form-control"
								name="password"
								v-model="loginPassword"
								:placeholder="$t('MAIL_LBL')"
								required="required">
						</div>
						<div class="form-group">
							<button type="button" class="btn btn-primary btn-lg btn-block"
								v-on:click="loginUser()">
								{{ $t('LOGIN_BTN') }}
							</button>
						</div>
					</div>
				</div>
				<div class="modal-footer">
					<div class="already">
						<div class="already-item">
							<p>{{ $t('SIGNUP_ACTION_LBL') }}</p>
							<a :href="endpoints.sessions_signup">{{ $t('REGISTER_BTN') }}</a>
						</div>
						<div class="already-item">
							<a :href="endpoints.forgot_password">{{ $t('FORGOT_PASWWORD_BTN') }}</a>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import {mapState, mapGetters, mapActions} from 'vuex';

export default {
	name: 'SessionsLogin',
	props: {
		endpoints: {
			type: Object,
			required: true
		}
	},
	data () {
		return {
			loginEmail: '',
			loginPassword: ''
		}
    },
	computed: {
		...mapState({
			user: state => state.user.profile
		})
    },
	methods: {
		...mapActions({
			login: 'user/login',
			logout: 'user/logout',
			notify: 'notification/notify'
		}),
		loginUser() {
			let data = {
				email: this.loginEmail,
				password: this.loginPassword
			}

			let btn = document.getElementById('user-session-modal-dismiss');
			let message = this.$t('SESSIONS_MSG_LOGIN_SUCESS');

			this.login(data)
				.then((user) => {
					btn.click();
					this.notify({
						message: message,
						type: 'success'
					});
				});
		}
    }
}
</script>
