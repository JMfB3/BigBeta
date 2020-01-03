"""
Routes for anything posts related
"""

from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from bigbeta import db
from bigbeta.models import Post
from bigbeta.posts.forms import PostForm


posts = Blueprint('posts', __name__)


@posts.route("/feedback")
def feedback():
    """
    Feedback page route
    """

    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('feedback.html', posts=posts)
    else:
        return redirect(url_for("users.login"))


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    """
    Route for new post / creating a post
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post created!", 'success')
        return redirect(url_for("posts.feedback"))
    return render_template('create_post.html', title='New Post',
                           form=form,
                           legend='New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    """
    Route for a single post
    """
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form,
                           legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!', 'success')
    return redirect(url_for('main.home'))
