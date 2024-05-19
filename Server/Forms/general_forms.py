from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import (
    StringField,
    SubmitField,
    FileField,
    PasswordField,
    TextAreaField,
    SelectField,
)
from wtforms.validators import DataRequired, Email
from data.DataStorage import DataStorage

# singleton instance of the DataStorage class
data_storage = DataStorage()


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
    submit = SubmitField("Submit")


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


class PromptAddForm(FlaskForm):
    prompt_field = StringField("Add Prompt", validators=[DataRequired()])
    submit = SubmitField("Add")


class PromptDeleteForm(FlaskForm):
    prompt_field = SelectField(label="Select prompt to delete")
    submit = SubmitField("Delete")
