from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, FileField, PasswordField, TextAreaField, SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, Email, ValidationError, Regexp
from app.Server.data.DataStorage import Data


class CloneAttackForm(FlaskForm):
    submit = SubmitField("Submit")


class AiAttackForm(FlaskForm):

    def validate_message_name(self, field):
        if self.message_type.data == "Email":
            try:
                Email(field)
            except ValidationError:
                raise ValidationError("Invalid email address.")
        else:
            phone_validator = Regexp(r'^\+972\d{9}$')
            try:
                # Manually apply the regular expression validator
                phone_validator.__call__(self, field)
            except ValidationError:
                # Raise a validation error if the phone number doesn't match the pattern
                raise ValidationError("Invalid phone number format. It should start with +972 and be followed "
                                      "by 9 digits.")

    campaign_name = StringField(
        label="Campaign Name",
        validators=[DataRequired()],
        default="Demo attack"
    )
    # mimic_profile = SelectField(
    #     label="Mimic Profile",
    #     validators=[DataRequired()],
    # )
    # target_profile = SelectField(
    #     label="Target Profile",
    #     validators=[DataRequired()],
    # )
    target_name = StringField(
        label="Target Name(Full name recommended)",
        validators=[DataRequired()],
        default="Aviv Nataf"
    )

    message_type = SelectField(
        label="Message Type",
        choices=[("Whatsapp", "Whatsapp"), ("Email", "Email")],
        default="Whatsapp"
    )

    message_name = StringField(
        label="message name (Whatsapp phone for whatsapp with +972 prefix, and email address for email)",
        validators=[validate_message_name],
        default="+972522464648"
    )

    attack_purpose = SelectField(
        label="Attack Purpose (Bank for account number, Delivery for address,"
              " Hospital for Id)",
        choices=[("Bank", "Bank"), ("Delivery", "Delivery"),
                 ("Hospital", "Hospital")],
        default="Bank"
    )
    place = StringField(
        label="Place (This represents the place the AI calls from, e.g. Bank name for "
              "Bank, Airport name for Delivery, and Hospital name for Hospital. The place should be related to the "
              "target)",
        validators=[
            Regexp(r'^[A-Za-z]+( [A-Za-z]+)*$', message="Place must contain words separated by a single space, "
                                                        "and start and end with a letter."),
            # Reference the custom validator method without `self`
        ],
        default="Discount"
    )
    # phone_number = StringField('Phone Number', validators=[
    #     DataRequired(),
    #     Regexp(r'^\+972\d{9}$', message="Please enter a valid phone number with the +972 prefix")
    # ])

    # campaign_description = TextAreaField(
    #    label="Campaign Description",
    #    validators=[DataRequired()],
    #    default="This is the campaign description"
    # )
    submit = SubmitField("Submit")


class ViewAttacksForm(FlaskForm):
    attack_list = SelectField(
        label="Select Attack",
        choices=Data().get_data_object().get_ai_attacks(),
        validators=[DataRequired()],
    )
    submit = SubmitField("View Info")


class AttackDashboardForm(FlaskForm):
    prompt_field = SelectField(
        label="Select prompt to activate",
        validators=[DataRequired()],
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
        label="Email address",
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
    email = StringField(label="Enter email for login",default="odedwar@gmail.com", validators=[Email()])
    submit = SubmitField("Login")


class AuthenticationForm(FlaskForm):
    code = StringField(label='Your code here:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField('Register')


class ZoomMeetingForm(FlaskForm):
    meeting_name = StringField('Meeting Name', default="Deceptify meeting", validators=[DataRequired()])
    year = IntegerField('Year', default=2024)
    month = IntegerField('Month', default=9)
    day = IntegerField('Day', default=2)
    hour = IntegerField('Hour', default=18)
    minute = IntegerField('Minute', default=0)
    second = IntegerField('Second', default=0)
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
    runs_on = SelectField(
        label="The Attack Will Run On",
        choices=[("Local Chat", "Local Chat"),
                 ("Telegram", "Telegram"),
                 ("WhatsApp", "WhatsApp")]
    )
    profile_name = StringField('The name of the mimic for the Demo',
                               validators=[DataRequired()])
    submit = SubmitField("Submit")


class TelegramClientBasicForm(FlaskForm):
    app_id = StringField("Your App API", validators=[DataRequired()])
    app_hash = StringField("Your App Hash", validators=[DataRequired()])
    profile_name = StringField("Your profile name", validators=[DataRequired()])
    phone_number = StringField("Your phone number", validators=[DataRequired()])

    submit = SubmitField("Submit")


class TelegramClientAdvancedForm(FlaskForm):
    target_name = StringField("Your target name on Telegram", validators=[DataRequired()])
    attack_purpose = StringField("Your attack purpose", validators=[DataRequired()])
    clone_voice_for_record = BooleanField("Cloning voice for send recording to the target")

    submit = SubmitField("Submit")
