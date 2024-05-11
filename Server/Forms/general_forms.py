from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, FileField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email

# omer 11/5/24 added get_profiles function to allow easy debug will be removed before final merge
# created CampaignForm allows user to name the campaign, choose mimic and target profiles
#  and write a description, also creates unique campaign id see routes.py line 63

def get_profiles(attacker=False):
    if attacker:
        return [('Attacker', 'Oded'), ('Attacker', 'Hadar')]
    else:
        return [('Victim', 'Bibi'), ('Victim', 'Bugs Bunny')]
    
class CampaignForm(FlaskForm):
    campaign_name = StringField("Campaign Name", validators=[DataRequired()])
    mimic_profile = SelectField("Mimic Profile", choices=get_profiles(attacker=True), validators=[DataRequired()])
    target_profile = SelectField("Target Profile", choices=get_profiles(), validators=[DataRequired()])
    campaign_description = TextAreaField("Campaign Description", validators=[DataRequired()])
    submit = SubmitField('Submit')

class AttackDashboardForm(FlaskForm):
    submit = SubmitField('Submit')


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
    gen_info_field = StringField("General Information", description="Enter any general information here", validators=[DataRequired()])

    # Additional fields to upload different types of data
    recording_upload = FileField(label='Upload Your Voice Recording', validators=[
        FileRequired(),
        FileAllowed(['mp3', 'wav', 'ogg'], 'Voice recording files only (MP3, WAV, OGG)')
    ])

    # dataset_upload = FileField('Upload Dataset')
    # video_upload = FileField('Upload Video')

    submit = SubmitField('Submit')





