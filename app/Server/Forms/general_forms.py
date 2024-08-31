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
        choices=[("Bank", "Bank"), ("Hospital", "Hospital"), ("Delivery", "Delivery")],
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


class ProfileForm(FlaskForm):
    name_field = StringField(
        label="Profile Name",
        validators=[DataRequired()]
    )

    selection = SelectField(
        label="Choose your type of recording",
        choices=[("Record", "Record"), ("Upload", "Upload")],
        validators=[DataRequired()],
    )  # Selection tag for choosing which kind of uploading the user prefer.
    
    submit = SubmitField("Submit")



class UploadForm(FlaskForm):
    # Additional fields to upload different types of data
    upload_file = FileField(
         label="Upload Your Voice Recording( WAV files )",
         validators=[
             FileRequired(),
             FileAllowed(
                 ["wav"], "WAV files only"
             ),
         ],
    )
    submit = SubmitField("Submit")


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
