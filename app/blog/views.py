from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify, abort, Response
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from flask.ext.paginate import Pagination
from flask.ext.babel import lazy_gettext, gettext
from app import app, login_manager, store, babel
from app.users.models import User
from app.posts.models import Post
from app.comments.models import Comment
from app.comments.forms import CommentForm
from config import LANGUAGES

@app.before_request
def before_request():
    if request.endpoint in ['index','show_post']:
        g.user_count = User.count()
        g.post_count = Post.count()
        g.comment_count = Comment.count()
    if 'redirect_to' in session and request.endpoint and request.endpoint not in ['static', 'sessions.login','sessions.signup','sessions.login_comment']:
        session.pop('redirect_to', None)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())

@babel.timezoneselector
def get_timezone():
    if current_user and current_user.is_authenticated():
        return current_user.timezone
    return "Asia/Tokyo"

@app.errorhandler(401)
def internal_error(error):
    return render_template('admin/401.html', title= 'Error %s' % error), 401

@app.errorhandler(403)
def internal_error(error):
    return render_template('admin/403.html', title= 'Error %s' % error), 403

@app.errorhandler(404)
def internal_error(error):
    return render_template('admin/404.html', title= 'Error %s' % error), 404

@app.errorhandler(500)
def internal_error(error):
    store.rollback()
    return render_template('admin/500.html', title= 'Error %s' % error), 500

@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page=1):
    limit = 5
    posts, count = Post.pagination(limit=limit,page=page)
    pagination = Pagination(page=page, 
        per_page= limit, 
        total= count, 
        record_name= gettext('posts'), 
        alignment = 'right', 
        bs_version= 3)
    return render_template("blog/index.html",
        title = gettext('Home'),
        posts = posts,
        pagination = pagination)

@app.route('/post/<int:id>', methods = ['GET','POST'])
def show_post(id):
    try:
        post = Post.get_by_id(id)
    except:
        post = None

    if post is None:
        abort(404)

    if request.method == 'POST':
        if not current_user.is_authenticated():
            abort(401)
        form = CommentForm()
        if form.validate_on_submit():
            try:
                comment = Comment.create()
                form.populate_obj(comment)
                comment.user = current_user
                comment.post = post
                comment.save()
                flash(gettext('Comment succesfully created'))
                return redirect('%s#comment_%s' % (url_for('show_post', id=post.id),comment.id) )
            except:
                flash(gettext('Error while posting the new comment, please retry later'), 'error')
        else:
            flash(gettext('Invalid submission, please check the message below'), 'error')
    else:
        # Hides the form when the user is not authenticated
        # Limit the number of comments per post
        if not current_user.is_authenticated() or post.comments.count() > 50: 
            form = None
        else:
            form = CommentForm()

    return render_template("blog/post-detail.html",
        title = gettext('Post | %(title)s',title=post.title),
        post = post,
        form = form)

@app.route('/post/<int:post_id>/comment/<int:id>/', methods = ['GET','POST'])
@login_required
def reply_comment(post_id, id):
    try:
        comment = Comment.get_by_id(id)
    except:
        comment = None

    try:
        post = Post.get_by_id(post_id)
    except:
        post = None        

    if comment is None or post is None:
        abort(403)

    form = CommentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                reply = Comment.create()
                form.populate_obj(reply)
                reply.user = current_user
                reply.post = post
                reply.reply = comment
                
                reply.save()
                flash(gettext('Comment succesfully created'))
                return redirect('%s#comment_%s' % (url_for('show_post', id=post.id),reply.id) )
            except:
                flash(gettext('Error while posting the new comment, please retry later'), 'error')
        else:
            flash(gettext('Invalid submission, please check the message below'), 'error')
        return redirect( url_for('show_post',id=post.id))
    else:
        form = CommentForm()

    tmplt = render_template("blog/post_form.js",
        comment = comment,
        form = form,
        postid=post.id)
    resp = Response(tmplt, status=200, mimetype='text/javascript')
    return resp
