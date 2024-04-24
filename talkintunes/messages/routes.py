from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from talkintunes import db
from talkintunes.messages.utils import text_to_note
from talkintunes.models import Messages, User
from talkintunes.users.utils import encrypt_message, decrypt_message

message = Blueprint('messages', __name__)


@login_required
@message.route("/messages/<peer_id>", methods=['GET','POST'])
def messages(peer_id):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    messages = Messages.query.filter(or_(
        and_(Messages.sender_id == peer_id, Messages.receiver_id == current_user.id),
        and_(Messages.receiver_id == peer_id, Messages.sender_id == current_user.id)
    )).all()

    return render_template('messages.html', messages=messages, title='Messages', user=user, peer_id=peer_id)


@message.route('/decrypt_message/<message_id>')
def decrypt_message(message_id):
    with open(current_user.private_key, 'rb') as f:
        private_key_pem = f.read()
    message_content = Messages.query.filter_by(id=message_id).with_entities(Messages.content).first()[0]
    decrypted_message = decrypt_message(message_content, private_key_pem)

@login_required
@message.route('/send_message/<peer_id>', methods=['POST'])
def send_message(peer_id):
    message = request.form['message']
    mp3_file_path = text_to_note(message, current_user)
    # mp3_file_path= f'static\\{mp3_file_name}'
    recipient_public_key = User.query.filter_by(id=peer_id).with_entities(User.public_key).first()
    if not recipient_public_key:
        return 'Recipient not found', 404
    else:
        recipient_public_key = recipient_public_key[0]

    # Encrypt message with recipient's public key
    recipient_public_key_bytes = recipient_public_key.encode('utf-8')
    encrypted_message = encrypt_message(message, recipient_public_key_bytes)

    msg = Messages(content=encrypted_message,
                   sender_id=current_user.id,
                   receiver_id=int(peer_id),
                   mp3_file_path=mp3_file_path)
    db.session.add(msg)
    db.session.commit()

    return redirect(url_for('messages.messages', peer_id=peer_id))
