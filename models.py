from datetime import datetime
from extensions import db

# Userクラスは不要になるため削除またはコメントアウト
# class User(db.Model, UserMixin):
#     ...

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # user_id を削除（誰でもアップロード可能にするため）
    captions = db.relationship('Caption', backref='image_ref', lazy=True)
    file_hash = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return f"Image('{self.filename}', '{self.upload_date}')"

class Caption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    generated_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)

    def __repr__(self):
        return f"Caption('{self.text[:20]}...')"