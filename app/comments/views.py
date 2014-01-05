from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify, abort, Response
from flask.ext.login import current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form
from flask.ext.babel import lazy_gettext, gettext
from app import app, login_manager
from flask.ext.paginate import Pagination
from app.comments.models import Comment
from forms import CommentForm, NewCommentForm, EditCommentForm

class CommentsView(FlaskView):
    route_base = '/comments'
    decorators = [login_required]

    def index(self):
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        limit = 10
        comments, count = Comment.pagination(page=page, limit=limit)

        pagination = Pagination(page=page, 
            per_page= limit, 
            total= count, 
            record_name= gettext('posts'), 
            alignment = 'right', 
            bs_version= 3)

        
        return render_template('admin/comments/index.html', 
            title = gettext('Comments | %(page)s', page=page),
            comments = comments,
            pagination = pagination)

    def get(self,id):
        comment = Comment.get_by_id(id)
        if comment is None:
            flash(gettext('The comment was not found'), 'error')
            return redirect(url_for('CommentsView:index'))

        return render_template('admin/comments/show.html', 
            title = gettext('Comment %(id)s', id=comment.id),
            comment = comment)

    @route('/<int:id>', methods = ['PUT'])
    @route('/edit/<int:id>', methods = ['GET', 'POST'])
    def put(self, id):
        comment = Comment.get_by_id(id)
        if comment is None:
            if request.is_xhr:
                abort(404)
            else:
                flash(gettext('The comment was not found'), 'error')
                return redirect(url_for('CommentsView:index'))
        if not comment.can_edit():
            abort(401)

        if request.method in ['POST','PUT']:
            
            if request.is_xhr:
                try:
                    data = request.get_json()
                    comment.body = unicode(data.body)
                    comment.save()
                    js = [ { "result": "ok" ,"type": "comment", "id" : comment.id, "body" : comment.body, "redirect": url_for('CommentsView:index') } ]
                    return Response(json.dumps(js),  mimetype='application/json')
                except:
                    js = [ { "result": "error" ,"type": "comment", "message" : gettext("Error while updating the comment") } ]
                    return Response(json.dumps(js),  mimetype='application/json')
            else:
                form = EditCommentForm()
                if form.validate_on_submit():
                    try:
                        form.populate_obj(comment)
                        comment.save()
                        flash(gettext('Comment was succesfully saved'))
                        if form.remain.data:
                            return redirect(url_for('CommentsView:get', id=comment.id))
                        else:
                            return redirect(url_for('CommentsView:index'))
                    except:
                        flash(gettext('Error while updating the comment'),'error')
                else:
                    message = gettext('Invalid submission, please check the message below')
                
        else:
            form = NewCommentForm(comment)

        return render_template('admin/comments/edit.html',
            title = gettext('Edit Comment: %(id)s', id=comment.id),
            form = form,
            comment = comment)

    @route('/<int:id>', methods = ['DELETE'])
    @route('/remove/<int:id>', methods = ['POST'])
    def delete(self,id):
        comment = Comment.get_by_id(id)
        if comment is None:
            if request.is_xhr:
                abort(404)
            else:
                flash(gettext('The comment was not found'), 'error')
                return redirect(url_for('CommentsView:index'))
        if not comment.can_edit():
            abort(401)
        message = ""
        try:
            Comment.safe_delete(comment)
            if request.is_xhr:
                js = [ { "result": "ok" , "type": "comment", "redirect": url_for('CommentsView:index') } ]
                return Response(json.dumps(js),  mimetype='application/json')
            else:
                flash(gettext('Comment removed'))
                return redirect(url_for('CommentsView:index'))
        except:            
            if request.is_xhr:
                js = [ { "result": "error" , "type": "comment", "redirect": url_for('CommentsView:index') } ]
                return Response(json.dumps(js),  mimetype='application/json')
            else:
                flash(gettext('Error while removing the comment'), 'error')
                return redirect(url_for('CommentsView:get', id=comment.id))



