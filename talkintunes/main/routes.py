from flask import Blueprint, render_template, request

from talkintunes.models import Messages

main = Blueprint('main', __name__)



@main.route('/')
@main.route('/home')
def home():
    # page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
    return render_template('home.html', title='Home')



@main.route('/about')
def about():
    return render_template('about.html')
