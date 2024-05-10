from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, FileField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email


class InformationGatheringForm(FlaskForm):
    selection = SelectField(label="Which type of information do you want to upload?",
                            choices=['DataSets', 'Recordings', 'Video'],
                            validators=[DataRequired()])
    submit = SubmitField('Submit')


class ContactForm(FlaskForm):
    email = StringField("Email", validators=[Email()])
    contact_field = TextAreaField("What's your thought?", validators=[DataRequired()])
    passwd = PasswordField('Enter you key for validation', validators=[DataRequired()])
    submit = SubmitField('Submit')


class VoiceChoiceForm(FlaskForm):
    selection = SelectField(label="Choose your type of recording", choices=['Record', 'Upload'], validators=[
        DataRequired()])  # Selection tag for choosing which kind of uploading the user prefer.
    passwd = PasswordField('Enter you key for validation', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ProfileForm(FlaskForm):
    name_field = StringField("Profile Name", validators=[DataRequired()])
    role_field = SelectField(label="Role",
                             choices=[('Victim', 'Victim'), ('Attacker', 'Attacker'), ('Other', 'Other')],
                             validators=[DataRequired()])
    data_type_selection = SelectField(label="Which type of information do you want to upload?",
                                      choices=[('DataSets', 'DataSets'), ('Recordings', 'Recordings'),
                                               ('Video', 'Video')],
                                      validators=[DataRequired()])

    # Additional fields to upload different types of data
    recording_upload = FileField(label='Upload Your Voice Recording', validators=[
        FileRequired(),
        FileAllowed(['mp3', 'wav', 'ogg'], 'Voice recording files only (MP3, WAV, OGG)')
    ])

    # dataset_upload = FileField('Upload Dataset')
    # video_upload = FileField('Upload Video')

    submit = SubmitField('Submit')


