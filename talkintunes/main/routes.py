from flask import Blueprint, render_template, request
from flask_login import current_user
from sqlalchemy import func, and_, or_

from talkintunes import db
from talkintunes.models import Messages, User

main = Blueprint('main', __name__)



@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=current_user.username).first_or_404()

    subquery = db.session.query(
        func.max(Messages.date).label("max_date"),
        func.least(Messages.sender_id, Messages.receiver_id).label("sorted_sender_id"),
        func.greatest(Messages.sender_id, Messages.receiver_id).label("sorted_receiver_id")
    ).group_by("sorted_sender_id", "sorted_receiver_id").subquery()

    # Join the Messages table with the subquery to get the complete message data for the last messages
    last_messages = db.session.query(Messages).join(
        subquery,
        and_(
            or_(
                Messages.sender_id == user.id,
                Messages.receiver_id == user.id
            ),
            func.least(Messages.sender_id, Messages.receiver_id) == subquery.c.sorted_sender_id,
            func.greatest(Messages.sender_id, Messages.receiver_id) == subquery.c.sorted_receiver_id,
            Messages.date == subquery.c.max_date
        )
    ).all()
    all_users = User.query.with_entities(User.username, User.id).all()


    return render_template('user_messages.html', messages=last_messages,
                           title='Messages', user=user, all_users=all_users)


@main.route('/about')
def about():
    return render_template('about.html')
