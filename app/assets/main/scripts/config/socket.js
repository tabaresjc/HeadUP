'use strict';

import io from 'socket.io-client';

const options = {
	transports: ['websocket']
};

export default io(options);
