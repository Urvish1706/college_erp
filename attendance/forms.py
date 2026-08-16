from django import forms


class AttendanceFilterForm(forms.Form):

    subject = forms.ModelChoiceField(
        queryset=None,
        empty_label="Select Subject",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )

    def __init__(self, *args, subjects=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["subject"].queryset = (
            subjects if subjects is not None else
            self.fields["subject"].queryset.none()
        )