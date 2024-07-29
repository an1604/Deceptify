from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired
from wtforms import MultipleFileField


class VoiceUploadForm(FlaskForm):
    files = MultipleFileField(
        label="Upload Your Voice Recordings (wav files)",
        render_kw={"multiple": True},
        validators=[
            FileRequired(),
            FileAllowed(['wav', 'mp3', 'wav'])],
    )
    submit = SubmitField("Submit")


class DataSetUploadForm(FlaskForm):
    file_field = FileField(
        label="Upload Your DataSet",
        validators=[
            FileRequired(),
            FileAllowed(
                ["csv", "txt", "pdf"], "Supported Dataset file types: CSV, TXT"
            ),
        ],
    )
    submit = SubmitField("Submit")


class VideoUploadForm(FlaskForm):
    video_field = FileField(
        label="Upload Your Video",
        validators=[
            FileRequired(),
            FileAllowed(
                ["mp4", "avi", "mov"], "Supported video file types: MP4, AVI, MOV"
            ),
        ],
    )
    passwd = PasswordField("Enter you key for validation", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ImageUploadForm(FlaskForm):
    image_field = FileField(
        label="Upload Your Image",
        validators=[
            FileRequired(),
            FileAllowed(
                ["jpg", "jpeg", "png"], "Supported image file types: JPG, JPEG, PNG"
            ),
        ],
    )
    passwd = PasswordField("Enter you key for validation", validators=[DataRequired()])
    submit = SubmitField("Submit")


class TextUploadForm(
    FlaskForm
):  # For uploading dataset for the model's training and tuning.
    file_field = FileField(
        label="Upload Your Dataset for tuning the model",
        validators=[
            FileRequired(),
            FileAllowed(
                ["csv", "txt", "pdf"], "Supported datasets from only (CSV, TXT, PDF)"
            ),
        ],
    )
    passwd = PasswordField("Enter you key for validation", validators=[DataRequired()])
    submit = SubmitField("Submit")
