from django import forms
from .models import Node, Value
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'password']


class NodeForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = ['str_optimal', 'highest_optimal', 'lowest_optimal']

    def __init__(self, *args, **kwargs):
        super(NodeForm, self).__init__(*args, **kwargs)
        self.fields['str_optimal'].widget.attrs.update({
            'placeholder': ""
        })

        self.fields['highest_optimal'].widget.attrs.update({
            'placeholder': ''
        })

        self.fields['lowest_optimal'].widget.attrs.update({
            'placeholder': ''
        })


class ValueForm(forms.ModelForm):
    class Meta:
        model = Value
        fields = ['float_data_required', 'str_data_required', 'detail_required']

