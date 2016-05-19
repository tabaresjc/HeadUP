# -*- coding: utf8 -*-

import sys

lenargs = len(sys.argv)
if  2 == lenargs and sys.argv[1] == 'init':
    print "Init Database"
    from app import db
    db.create_all()
elif  5 == lenargs and sys.argv[1] == 'create_user':
    print "Create User"
    from app.users.models import User, Role
    name = sys.argv[2]
    email = sys.argv[3]
    password = sys.argv[4]
    email_parts = email.split('@')
    if len(email_parts) > 1:
        user = User.create(
            name=name,
            email=email,
            password='',
            nickname=email_parts[0],
            role_id=Role.ROLE_ADMIN,
            address=u'',
            phone=u'',
            lang='en'
        )
        user.set_password(unicode(password))
        user.save()
    else:
        print "Sorry! Can not create user :( "
