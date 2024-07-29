from wtforms.validators import ValidationError


def MultipleFileRequired(form, field):
    if not field.data:
        raise ValidationError('This field is required.')
    if isinstance(field.data, list) and len(field.data) == 0:
        raise ValidationError('This field is required.')
