import os
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from PIL import Image as PILImage 
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
import uuid
import hashlib
from dotenv import load_dotenv

from extensions import db
# login_manager のインポートを削除
# from flask_login import login_required, current_user 

# 認証用ブループリントのインポートを削除
# from auth import auth_bp

# User モデルのインポートを削除（認証を使わない場合）
from models import Image, Caption 

load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"

# モデルとプロセッサ、トークナイザーのロード
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning").to(device)
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

def generate_caption(image_path):
    """画像パスを受け取り、AIで英文キャプションを生成する関数"""
    try:
        i_image = PILImage.open(image_path)
        if i_image.mode != "RGB":
            i_image = i_image.convert(mode="RGB")

        pixel_values = feature_extractor(images=[i_image], return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        # キャプション生成の設定
        gen_kwargs = {"max_length": 16, "num_beams": 4}
        output_ids = model.generate(pixel_values, **gen_kwargs)
        preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        preds = [pred.strip() for pred in preds]
        return preds[0]
    except Exception as e:
        print(f"Prediction Error: {e}")
        return "Caption generation failed."

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key_if_env_not_set') 

# app.py の設定部分
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'sqlite:///instance/site.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db.init_app(app) 

with app.app_context():
    # プログラム起動時に、models.pyの内容に従ってテーブルを自動作成します
    db.create_all()

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ブループリントの登録を削除
# app.register_blueprint(auth_bp, url_prefix='/auth') 

# ... (AIモデルのロード部分などはそのまま) ...
@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None
    caption_text_generated = None
    
    if request.method == 'POST':
        # 1. リクエストの中に 'file' というキーがあるか確認
        if 'file' not in request.files:
            flash("ファイルが選択されていません。", "error")
            return redirect(request.url)

        # 2. ここで 'file' 変数を定義する（これがないと NameError になります）
        file = request.files['file']

        # 3. ファイル名が空でないか確認
        if file.filename == '':
            flash("ファイルが選択されていません。", "error")
            return redirect(request.url)

        # 4. ここで file 変数を使って処理を開始
        if file:
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in file.filename or \
               file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                flash("許可されていないファイル形式です。", "error")
                return redirect(request.url)

            # ファイル保存用の名前生成
            filename_original = file.filename
            filename_uuid = str(uuid.uuid4()) + os.path.splitext(filename_original)[1]
            filepath_on_server = os.path.join(app.config['UPLOAD_FOLDER'], filename_uuid).replace("\\","/")
            
            try:
                # ハッシュチェック
                file_content = file.read()
                file_hash = hashlib.sha256(file_content).hexdigest()
                file.seek(0) # 保存するためにポインタを先頭に戻す

                # 重複チェック（任意ですが既存コードに合わせて記載）
                existing_image = Image.query.filter_by(file_hash=file_hash).first()
                if existing_image:
                    flash("この画像は既にアップロードされています！", "warning")
                    image_url = url_for('uploaded_file', filename=os.path.basename(existing_image.filepath))
                    if existing_image.captions:
                        caption_text_generated = existing_image.captions[0].text
                    return render_template('index.html', image_url=image_url, caption=caption_text_generated)

                # ファイルの保存
                file.save(filepath_on_server)
                image_url = url_for('uploaded_file', filename=filename_uuid)

                # AIによるキャプション生成
                caption_text_generated = generate_caption(filepath_on_server)
                
                # データベース保存 (user_id=1 を固定で使用)
                new_image = Image(
                    filename=filename_original,
                    filepath=filepath_on_server,
                    file_hash=file_hash 
                )
                db.session.add(new_image)
                db.session.commit()

                new_caption = Caption(
                    text=caption_text_generated,
                    image_id=new_image.id
                )
                db.session.add(new_caption)
                db.session.commit()

                flash("キャプションが生成されました！", "success")

            except Exception as e:
                print(f"Error: {e}")
                flash(f"エラーが発生しました: {e}", "error")

    return render_template('index.html', image_url=image_url, caption=caption_text_generated)
# ギャラリーからも @login_required を外す
@app.route('/gallery')
def gallery():
    images = Image.query.all()
    for img in images:
        filename = os.path.basename(img.filepath)
        img.url = url_for('uploaded_file', filename=filename)
    return render_template('gallery.html', images=images)

# これがないと画像URL（/static/uploads/xxx.jpg）にアクセスしても 404 エラーになります
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)