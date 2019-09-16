'use strict';

import { GetLanguage } from 'Assets/helpers';
import moment from 'moment';
import 'moment/locale/es';
import 'moment/locale/fr';
import 'moment/locale/ja';

let m = null;

export function MomentInstance() {
	if (!m) {
		m = moment;
		let lang = GetLanguage();
		m.locale(lang);
	}
	return m;
}
