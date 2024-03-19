from django import forms
from .models import Document, Image, Summary, Tag, Related, Vector, QA, Feedback, Query, PDF

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']  # List all the fields you want from the model


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['document_id', 'file_path']  # List all the fields you want from the model



class SummaryForm(forms.ModelForm):
    class Meta:
        model = Summary
        fields = ['document_id', 'summary']  # Assuming these are the fields you need

    def __init__(self, *args, **kwargs):
        super(SummaryForm, self).__init__(*args, **kwargs)
        self.fields['document_id'].widget.attrs.update({'placeholder': 'Insert docId here'})
        self.fields['document_id'].help_text = 'Enter the docId assigned by the API upon PDF upload.'
        # Assuming summary field is for displaying summary and not for user input:
        self.fields['summary'].widget.attrs.update({'placeholder': 'This will display your summary'})
        self.fields['summary'].disabled = True
        self.fields['summary'].help_text = 'Summary results will appear here after submission.'

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['document_id', 'tag']  # List all the fields you want from the model


class RelatedForm(forms.ModelForm):
    class Meta:
        model = Related
        fields = ['document_id', 'related_document_id']  # List all the fields you want from the model


class VectorForm(forms.ModelForm):
    class Meta:
        model = Vector
        fields = ['document_id', 'vector']  # List all the fields you want from the model


class QAForm(forms.ModelForm):
    class Meta:
        model = QA
        fields = ['document_id', 'question', 'answer']  # List all the fields you want from the model


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['document_id', 'feedback']  # List all the fields you want from the model


class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['document_id', 'query']  # List all the fields you want from the model


class PDFForm(forms.ModelForm):
    class Meta:
        model = PDF
        fields = ['file_name', 'text_content', 'related_docs', 'summary', 'tags', 'category', 'author', 'source', 'images', 'vector_representation', 'question_answer_pairs', 'user_queries', 'feedback']  # List all the fields you want from the model

class SearchForm(forms.Form):
    search = forms.CharField(max_length=100)

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

class UploadForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
    



class UploadPDFUrlForm(forms.Form):
    url = forms.URLField(label='PDF URL', required=True)
    isPrivate = forms.BooleanField(label='Is Private', required=False, initial=False)
    ocr = forms.BooleanField(label='Enable OCR', required=False, initial=False)


class UploadPDFForm(forms.Form):
    file = forms.FileField(label='PDF File', required=True)
    isPrivate = forms.BooleanField(label='Is Private', required=False, initial=False)
    ocr = forms.BooleanField(label='Enable OCR', required=False, initial=False)













class PDFAnalysisForm(forms.Form):
    ANALYSIS_CHOICES = [
        ('text_extraction', 'Text Extraction'),
        ('ocr', 'Optical Character Recognition (OCR)'),
        ('content_summarization', 'Content Summarization'),
        ('data_extraction', 'Data Extraction'),
        ('document_classification', 'Document Classification'),
        ('sentiment_analysis', 'Sentiment Analysis'),
    ]

    analysis_type = forms.ChoiceField(choices=ANALYSIS_CHOICES, required=True)

# forms.py

# forms.py


class ChatForm(forms.Form):
    message = forms.CharField(
        label='Your Message',
        max_length=1000,  # Adjust the max_length as needed
        widget=forms.Textarea(attrs={'placeholder': 'Type your message here...'}),
        required=True
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




# Compare this snippet from myproject/research_support/views.py:
        
# def upload(request):
#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)

#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('pdfs'))
#     else:
#         form = DocumentForm()



#     return render(request, 'research_support/upload.html', {
    
#         'form': form
#     })

# def upload_image(request):

#     if request.method == 'POST':

