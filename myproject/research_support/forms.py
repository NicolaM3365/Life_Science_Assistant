from django import forms
from .models import Summary, PDF, ChatHistory

class SearchForm(forms.Form):
    search = forms.CharField(max_length=100)




class UploadPDFUrlForm(forms.Form):
    url = forms.URLField(label='PDF URL', required=True)
    isPrivate = forms.BooleanField(label='Is Private', required=False, initial=False)
    ocr = forms.BooleanField(label='Enable OCR', required=False, initial=False)


class UploadPDFForm(forms.Form):
    file = forms.FileField(label='PDF File', required=True)
    isPrivate = forms.BooleanField(label='Is Private', required=False, initial=False)
    ocr = forms.BooleanField(label='Enable OCR', required=False, initial=False)




# class PDFAnalysisForm(forms.Form):
#     ANALYSIS_CHOICES = [
#         ('text_extraction', 'Text Extraction'),
#         ('ocr', 'Optical Character Recognition (OCR)'),
#         ('content_summarization', 'Content Summarization'),
#         ('data_extraction', 'Data Extraction'),
#         ('document_classification', 'Document Classification'),
#         ('sentiment_analysis', 'Sentiment Analysis'),
#     ]

#     analysis_type = forms.ChoiceField(choices=ANALYSIS_CHOICES, required=True)

# forms.py

# forms.py
    
class DeletePDFForm(forms.Form):
    docId = forms.CharField(
        label='Document ID',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Paste the Document ID here...'})
    )

class ChatForm(forms.Form):
    docId = forms.CharField(
        label='Document ID',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Paste the Document ID here...'})  # Use TextInput for a one-line input box
    )
    message = forms.CharField(
        label='Message',
        required=True, 
        widget=forms.Textarea(attrs={'placeholder': 'Enter your message or question...'})  # Use TextInput for a one-line input box

    )


    save_chat = forms.BooleanField(
        label='Save Chat History',
        required=False,  # This field is not mandatory
        initial=False
    )

    # language = forms.ChoiceField(
    #     label='Response Language',
    #     choices=[('en', 'English'), ('fr', 'French'), ('es', 'Spanish'), ...],  # Add more languages as needed
    #     required=False,
    #     initial='en'
    # )

    use_gpt4 = forms.BooleanField(
        label='Use GPT-4 Model',
        required=False,
        initial=False
    )


class SummaryForm(forms.Form):
    docId = forms.CharField(
        label='Document ID',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Paste the Document ID here...',
            'class': 'form-control',  # Bootstrap class for styling
        }),
        help_text='Paste the docId assigned by the API upon PDF upload here...'
    )
    summary = forms.CharField(
        label='Summary',
        required=False,  # Set to False because the summary is provided by the API and not the user
        widget=forms.Textarea(attrs={
            'placeholder': 'This will display your summary',
            'class': 'form-control',  # Bootstrap class for styling
            'disabled': True,
            'rows': 4,
            'cols': 15
        }),
        help_text='Summary results will appear here after submission.'
    )





