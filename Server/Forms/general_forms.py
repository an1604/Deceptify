from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, FileField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError
from Server.data.DataStorage import DataStorage


class CampaignForm(FlaskForm):
    campaign_name = StringField("Campaign Name", validators=[DataRequired()])
    mimic_profile = SelectField("Mimic Profile", validators=[DataRequired()])
    target_profile = SelectField("Target Profile", validators=[DataRequired()])
    attack_type = SelectField(
        "Attack Type", choices=["Voice", "Video"], validators=[DataRequired()]
    )
    # attack_type = SelectField("Attack Type", choices=['Voice Call', 'Voice Recording', 'Video Call', 'Video Recording'], validators=[DataRequired()])
    campaign_description = TextAreaField(
        "Campaign Description", validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


class ViewAttacksForm(FlaskForm):
    attack_list = SelectField(
        "Select Attack", choices=DataStorage.get_attacks, validators=[DataRequired()]
    )
    submit = SubmitField("View Info")


class AttackDashboardForm(FlaskForm):
    prompt_field = SelectField(label="Select prompt to activate", validators=[DataRequired()])
    submit = SubmitField('Submit')


class InformationGatheringForm(FlaskForm):
    selection = SelectField(
        label="Which type of information do you want to upload?",
        choices=["DataSets", "Recordings", "Video"],
        validators=[DataRequired()],
    )
    submit = SubmitField("Submit")


class ContactForm(FlaskForm):
    email = StringField("Email", validators=[Email()])
    contact_field = TextAreaField("What's your thought?", validators=[DataRequired()])
    passwd = PasswordField("Enter you key for validation", validators=[DataRequired()])
    submit = SubmitField("Submit")


class VoiceChoiceForm(FlaskForm):
    selection = SelectField(
        label="Choose your type of recording",
        choices=["Record", "Upload"],
        validators=[DataRequired()],
    )  # Selection tag for choosing which kind of uploading the user prefer.
    passwd = PasswordField("Enter you key for validation", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ViewProfilesForm(FlaskForm):
    profile_list = SelectField(
        label="Select Profile",
        description="Select the profile you want to view, if empty create some!",
    )
    submit = SubmitField("View Profile")


class ProfileForm(FlaskForm):
    name_field = StringField("Profile Name", validators=[DataRequired()])
    role_field = SelectField(
        label="Role",
        choices=[("Victim", "Victim"), ("Attacker", "Attacker"), ("Other", "Other")],
        validators=[DataRequired()],
    )
    data_type_selection = SelectField(
        label="Which type of information do you want to upload?",
        choices=[
            ("DataSets", "DataSets"),
            ("Recordings", "Recordings"),
            ("Video", "Video"),
        ],
        validators=[DataRequired()],
    )
    gen_info_field = StringField(
        "General Information",
        description="Enter any general information here",
        validators=[DataRequired()],
    )

    # Additional fields to upload different types of data
    recording_upload = FileField(
        label="Upload Your Voice Recording",
        validators=[
            FileRequired(),
            FileAllowed(
                ["mp3", "wav", "ogg"], "Voice recording files only (MP3, WAV, OGG)"
            ),
        ],
    )

    # dataset_upload = FileField('Upload Dataset')
    # video_upload = FileField('Upload Video')

    submit = SubmitField("Submit")


def validate_add_prompt(form, field):
    prompt = field.data
    for prt in form.profile.getPrompts():
        if prompt == prt.prompt_desc:
            raise ValidationError('This prompt already exist')


class PromptAddForm(FlaskForm):
    prompt_add_field = StringField("Add Prompt", validators=[DataRequired(), validate_add_prompt])
    submit_add = SubmitField('Add')

    def __init__(self, *args, **kwargs):
        # Extract the extra argument
        self.profile = kwargs.pop('profile', None)
        super(PromptAddForm, self).__init__(*args, **kwargs)


def validate_delete_prompt(form, field):
    prompt = field.data
    for prt in form.profile.getPrompts():
        if prompt == prt.prompt_desc:
            if not prt.is_deletable:
                raise ValidationError('This prompt cannot be deleted')
            return


class PromptDeleteForm(FlaskForm):
    prompt_delete_field = SelectField(label="Select prompt to delete",validators=[validate_delete_prompt])
    submit_delete = SubmitField('Delete')

    def __init__(self, *args, **kwargs):
        # Extract the extra argument
        self.profile = kwargs.pop('profile', None)
        super(PromptDeleteForm, self).__init__(*args, **kwargs)
