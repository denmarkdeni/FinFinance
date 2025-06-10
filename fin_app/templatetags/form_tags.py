from django import template

register = template.Library()

@register.filter(name='as_input')
def as_input(field, placeholder=""):
    return field.as_widget(attrs={
        'class': 'form__input',
        'placeholder': placeholder
    })

@register.filter(name='as_select')
def as_select(field, css_class="form__select"):
    return field.as_widget(attrs={'class': "form__input"})
