from unfold.forms import UserChangeForm, UserCreationForm

from apps.auths.models import User

class CustomUserChangeForm(UserChangeForm):
    """edit form. our user has no 'username', so we set our own model"""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
        field_classes = {}


class CustomUserCreationForm(UserCreationForm):
    """add form: email, first_name, last_name, password1, password2"""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name")
        field_classes = {}
