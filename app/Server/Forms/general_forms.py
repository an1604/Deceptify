from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, FileField, PasswordField, TextAreaField, SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, Email, ValidationError, Regexp
from app.Server.data.DataStorage import Data


class CampaignForm(FlaskForm):

    def validate_place(self, field):
        if self.voice_type.data == "AI" and not field.data:
            raise ValidationError("Place is required when Voice Type is set to AI.")

    campaign_name = StringField(
        label="Campaign Name",
        validators=[DataRequired()]
    )
    mimic_profile = SelectField(
        label="Mimic Profile",
        validators=[DataRequired()]
    )
    target_profile = SelectField(
        label="Target Profile",
        validators=[DataRequired()]
    )
    target_name = StringField(
        label="Target Name",
        validators=[DataRequired()]
    )
    voice_type = SelectField(
        label="Voice type (Clone for cloned voice attack, AI for default voice AI attack)",
        choices=[("Clone", "Clone"), ("AI", "AI")],
        validators=[DataRequired()]
    )
    attack_purpose = SelectField(
        label="Attack Purpose (Fill in case of AI attack. Bank for Id and account number, Delivery for address,"
              "Hospital for Id and address)",
        choices=[("Bank", "Bank"), ("Delivery", "Delivery"),
                 ("Hospital", "Hospital"), ("WhatsApp and Zoom", "WhatsApp and Zoom")],
        validators=[DataRequired()]
    )
    place = StringField(
        label="Place (Fill in case of AI attack. This represents the place the AI calls from, e.g. Bank name for "
              "Bank, Airport name for Delivery, and Hospital name for Hospital. The place should be related to the "
              "target)",
        validators=[
            validate_place,
            Regexp(r'^[A-Za-z]+( [A-Za-z]+)*$', message="Place must contain words separated by a single space, "
                                                        "and start and end with a letter."),
            # Reference the custom validator method without `self`
        ]
    )
    # phone_number = StringField('Phone Number', validators=[
    #     DataRequired(),
    #     Regexp(r'^\+972\d{9}$', message="Please enter a valid phone number with the +972 prefix")
    # ])
    campaign_description = TextAreaField(
        label="Campaign Description",
        validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


class ViewAttacksForm(FlaskForm):
    attack_list = SelectField(
        label="Select Attack",
        choices=Data().get_data_object().get_attacks(),
        validators=[DataRequired()]
    )
    submit = SubmitField("View Info")


class AttackDashboardForm(FlaskForm):
    prompt_field = SelectField(
        label="Select prompt to activate",
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit')


class InformationGatheringForm(FlaskForm):
    selection = SelectField(
        label="Which type of information do you want to upload?",
        choices=[("DataSets", "DataSets"), ("Recordings", "Recordings"), ("Video", "Video")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Submit")


class ContactForm(FlaskForm):
    email = StringField(
        label="llm_chat_tools",
        validators=[Email()]
    )
    contact_field = TextAreaField(
        label="What's your thought?",
        validators=[DataRequired()]
    )
    passwd = PasswordField(
        label="Enter you key for validation",
        validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


class VoiceChoiceForm(FlaskForm):
    selection = SelectField(
        label="Choose your type of recording",
        choices=[("Record", "Record"), ("Upload", "Upload")],
        validators=[DataRequired()],
    )  # Selection tag for choosing which kind of uploading the user prefer.
    passwd = PasswordField(
        label="Enter you key for validation",
        validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


class ViewProfilesForm(FlaskForm):
    profile_list = SelectField(
        label="Select Profile",
        description="Select the profile you want to view, if empty create some!",
    )
    submit = SubmitField("View Profile")


class ProfileForm(FlaskForm):
    name_field = StringField(
        label="Profile Name",
        validators=[DataRequired()]
    )
    gen_info_field = TextAreaField(
        "General info",
        description="Enter general info",
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

    Image_upload = FileField(
        label='Upload Video',
        validators=[FileAllowed(["JPG", "jpg"], message="JPG Images only")]
    )

    # dataset_upload = FileField('Upload Dataset')

    submit = SubmitField("Submit")


def validate_add_prompt(form, field):
    prompt = field.data
    for prt in form.profile.getPrompts():
        if prompt == prt.prompt_desc:
            raise ValidationError('This prompt already exist')


class PromptAddForm(FlaskForm):
    prompt_add_field = StringField(
        "Add Prompt",
        validators=[DataRequired(), validate_add_prompt]
    )
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
    prompt_delete_field = SelectField(
        label="Select prompt to delete",
        validators=[validate_delete_prompt]
    )
    submit_delete = SubmitField('Delete')

    def __init__(self, *args, **kwargs):
        # Extract the extra argument
        self.profile = kwargs.pop('profile', None)
        super(PromptDeleteForm, self).__init__(*args, **kwargs)


class LoginForm(FlaskForm):
    email = StringField(label="llm_chat_tools", validators=[Email()])
    submit = SubmitField("Login")


class AuthenticationForm(FlaskForm):
    code = StringField(label='Your code here:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ZoomMeetingForm(FlaskForm):
    meeting_name = StringField('Meeting Name', validators=[DataRequired()])
    year = IntegerField('Year', default=2024)
    month = IntegerField('Month')
    day = IntegerField('Day')
    hour = IntegerField('Hour')
    minute = IntegerField('Minute')
    second = IntegerField('Second', default=13)
    submit = SubmitField("Submit")


class DemoForm(FlaskForm):
    message = StringField('Type your message', validators=[DataRequired()])
    submit = SubmitField("Submit")


class InitDemoForm(FlaskForm):
    purpose = SelectField(
        label="Attack Purpose (Fill in case of AI attack. Bank for Id and account number, Delivery for address,"
              "Hospital for Id and address)",
        choices=[("Bank", "Bank"), ("Delivery", "Delivery"),
                 ("Hospital", "Hospital")],
        validators=[DataRequired()]
    )
    profile_name = StringField('The name of the mimic for the Demo',
                               validators=[DataRequired()])
    submit = SubmitField("Submit")

