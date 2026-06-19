# Testing wtforms stuff
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired



class TestForm(FlaskForm):
    course = SelectField('Course', choices=[
        ('', '-- Select a course --'),
        ('Python', '🐍 Python Programming'),
        ('WebDev', '🌐 Web Development'),
        ('DataScience', '📊 Data Science'),
        ('MachineLearning', '🤖 Machine Learning'),
        ('Other', '📚 Other')
    ], validators=[
        DataRequired(message='⚠️ Please select a course')
    ], render_kw={
        'class': 'form-control'
    })

class TestBookingForm(FlaskForm):
    status = SelectField("Status", choices=[
        ("PENDING", "PENDING"),
        ("APPROVED", "APPROVED"),
        ("CANCELED", "CANCELED"),
        ("EXPIRED", "EXPIRED")
    ],
    validators=[
        DataRequired()
    ],
    default="PENDING",
    render_kw={"class": "form-control"}
    )