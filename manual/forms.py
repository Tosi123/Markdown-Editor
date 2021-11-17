from django import forms

from mdeditor.fields import MDTextFormField


class DocumentForm(forms.Form):
    title = forms.CharField(label='제목', max_length=50)
    writer = forms.CharField(label='작성자', max_length=5)
    text = MDTextFormField(label='내용')


class DocumentModifyForm(forms.Form):
    title = forms.CharField(label='제목', max_length=50)
    writer = forms.CharField(label='작성자', max_length=5)
    text = MDTextFormField(label='내용')


class MediaForm(forms.Form):
    docfile = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}), label='파일을 선택 하세요')


class CategoryForm(forms.Form):
    title = forms.CharField(label='제목', max_length=50)
    real_path = forms.CharField(label='서버 경로')
