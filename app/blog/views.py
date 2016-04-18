from flask import render_template, flash, redirect, session, url_for, request, g, abort, Response
from flask.ext.login import current_user, login_required
from flask.ext.paginate import Pagination
from flask.ext.babel import gettext
from app import app, store, babel
from app.users.models import User
from app.posts.models import Post
from app.comments.models import Comment
from app.categories.models import Category
from app.comments.forms import CommentForm
from forms import SearchForm
from models import Search
from config import LANGUAGES


@app.before_request
def before_request():
    if request.endpoint:
        if 'redirect_to' in session and request.endpoint not in ['static', 'sessions.login', 'sessions.signup', 'sessions.login_comment']:
            session.pop('redirect_to', None)


@babel.localeselector
def get_locale():
    if current_user and current_user.is_authenticated():
        return current_user.lang
    return request.accept_languages.best_match(LANGUAGES.keys())


@babel.timezoneselector
def get_timezone():
    if current_user and current_user.is_authenticated():
        return current_user.timezone
    return "Asia/Tokyo"


@app.errorhandler(401)
def internal_error_401(error):
    return render_template('admin/401.html', title='Error %s' % error), 401


@app.errorhandler(403)
def internal_error_403(error):
    return render_template('admin/403.html', title='Error %s' % error), 403


@app.errorhandler(404)
def internal_error_404(error):
    g.searhform = SearchForm()
    return render_template('admin/404.html', title='Error %s' % error), 404


@app.errorhandler(500)
def internal_error_500(error):
    store.rollback()
    return render_template('admin/500.html', title='Error %s' % error), 500


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page=1):
    limit = 5
    posts, count = Post.pagination(limit=limit, page=page)
    pagination = Pagination(page=page,
        per_page=limit,
        total=count,
        record_name=gettext('posts'),
        alignment='right')

    return render_template("blog/index.html",
        title=gettext('Home'),
        posts=posts,
        pagination=pagination)


@app.route('/<string:cat>/<string:post>')
def show_article(cat, post):
    try:
        post = Category.get_by_cat_slug(cat, post)
    except:
        post = None

    if post is None:
        abort(404)

    if not current_user.is_authenticated() or post.comments.count() > 50:
        form = None
    else:
        form = CommentForm()

    return render_template("blog/post-detail.html",
        title=gettext('Post | %(title)s', title=post.title),
        post=post,
        form=form)


@app.route('/category/<string:cat>', defaults={'page': 1})
@app.route('/category/<string:cat>/<int:page>')
def show_category(cat, page=1):
    limit = 5
    posts, category = Category.get_posts_by_cat(cat, limit=limit, page=page)

    pagination = Pagination(page=page,
        per_page=limit,
        total=category.posts.count(),
        record_name=gettext('posts'),
        alignment='right',
        bs_version=3)
    return render_template("blog/index.html",
        title=category.name,
        posts=posts,
        pagination=pagination,
        category=category)


@app.route('/post/<int:id>/', methods=['GET', 'POST'])
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
                return redirect('%s#comment_%s' % (url_for('show_article',
                    cat=post.category.slug,
                    post=post.slug),
                comment.id))
            except:
                flash(gettext('Error while posting the new comment, please retry later'), 'error')
        else:
            flash(gettext('Invalid submission, please check the message below'), 'error')
    else:
        if not current_user.is_authenticated() or post.comments.count() > 50:
            form = None
        else:
            form = CommentForm()

    return render_template("blog/post-detail.html",
        title=gettext('Post | %(title)s', title=post.title),
        post=post,
        form=form)


@app.route('/post/<int:post_id>/comment/<int:id>/', methods=['GET', 'POST'])
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
                return redirect('%s#comment_%s' % (url_for('show_post', id=post.id), reply.id))
            except:
                flash(gettext('Error while posting the new comment, please retry later'), 'error')
        else:
            flash(gettext('Invalid submission, please check the message below'), 'error')
        return redirect(url_for('show_post', id=post.id))
    else:
        form = CommentForm()

    tmplt = render_template("blog/post_form.js",
        comment=comment,
        form=form,
        postid=post.id)
    resp = Response(tmplt, status=200, mimetype='text/javascript')
    return resp


@app.route('/search/', methods=['GET', 'POST'])
def search_post():
    form = SearchForm()
    posts = None
    count = 0
    limit = 5
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                posts, count = Search.search_post(form.searchtext.data, limit=limit, page=page)
                session['search_query'] = form.searchtext.data
            except:
                flash(gettext('Error while searching, please retry later'), 'error')
        else:
            flash(gettext('Invalid submission, please check the message below'), 'error')
    else:
        if 'search_query' in session:
            form.searchtext.data = session['search_query']
            try:
                posts, count = Search.search_post(form.searchtext.data, limit=limit, page=page)
            except:
                flash(gettext('Error while searching, please retry later'), 'error')

    pagination = Pagination(page=page,
        per_page=limit,
        total=count,
        record_name=gettext('posts'),
        alignment='right',
        bs_version=3)

    return render_template("blog/post-search.html",
        title=gettext('Search'),
        form=form,
        posts=posts,
        pagination=pagination)

@app.route('/stamp/create/', methods=['GET', 'POST'])
@login_required
def create_stamp():
    from app.posts.forms import PostForm
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                post = Post.create()
                form.populate_obj(post)
                post.user = current_user
                post.save()
                flash(gettext('Stamp succesfully created'))
                return redirect(url_for('index'))
            except:
                flash(gettext('Error while posting the new comment, please retry later'), 'error')
        else:
            flash(gettext('Invalid submission, please check the message below'), 'error')
        return redirect(url_for('show_post', id=post.id))
    else:
        form = PostForm()
    return render_template("blog/stamp/form.html", form=form)
