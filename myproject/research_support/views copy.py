import os
from django.shortcuts import render

import requests

# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from .models import PDF
from .models import Document
from .models import Image
from .models import Summary
from .models import Tag
from .models import Related
from .models import Vector
from .models import QA
from .models import Feedback
from .models import Query
from .forms import DocumentForm
from .forms import ImageForm
from .forms import SummaryForm
from .forms import TagForm
from .forms import RelatedForm
from .forms import VectorForm
from .forms import QAForm
from .forms import FeedbackForm
from .forms import QueryForm
from .forms import SearchForm
from .forms import UploadForm

from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordChangeView

from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import DetailView

from django.urls import reverse_lazy

from .models import PDF
from .forms import PDFForm, ImageForm, SummaryForm, TagForm, RelatedForm, VectorForm, QAForm, FeedbackForm, QueryForm, PDFAnalysisForm

import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from django.shortcuts import render, get_object_or_404

from .forms import ChatForm  # Assume you have a form for users to input their message



# from django.http import JsonResponse
# from .models import Document  # Assuming you have a Document model
# from .forms import DocumentForm  # Assuming you have a form for Document

# from django.views.generic import View
# from django.views.generic import TemplateView
# from django.views.generic import FormView
# from django.views.generic import UpdateView
# from django.views.generic import DeleteView

# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.mixins import PermissionRequiredMixin
# from django.contrib.auth.mixins import UserPassesTestMixin
# from django.contrib.auth.mixins import AccessMixin

# from django.contrib.auth.models import User
# from django.contrib.auth.models import Group
# from django.contrib.auth.models import Permission

# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.decorators import permission_required
# from django.contrib.auth.decorators import user_passes_test
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth import update_session_auth_hash
# from django.contrib.auth import get_user_model
# from django.contrib.auth import REDIRECT_FIELD_NAME
# from django.contrib.auth import views as auth_views

# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.forms import PasswordChangeForm

# from django.contrib.auth.views import LoginView
# from django.contrib.auth.views import LogoutView
# from django.contrib.auth.views import PasswordChangeView
# from django.contrib.auth.views import PasswordChangeDoneView
# from django.contrib.auth.views import PasswordResetView
# from django.contrib.auth.views import PasswordResetDoneView
# from django.contrib.auth.views import PasswordResetConfirmView
# from django.contrib.auth.views import PasswordResetCompleteView


# from django.contrib import messages
# from django.contrib.messages.views import SuccessMessageMixin
# from django.contrib.messages.views import messages as messages_views

# from django.utils.translation import gettext_lazy as _

# from django.utils.decorators import method_decorator
# from django.utils.decorators import classonlymethod
# from django.utils.decorators import decorator_from_middleware

# from django.utils.http import is_safe_url
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.utils.http import urlencode
# from django.utils.http import urlquote
# from django.utils.http import urlunquote
# from django.utils.http import urlunquote_plus
# from django.utils.http import urlquote_plus
# from django.utils.http import base36_to_int
# from django.utils.http import int_to_base36
# from django.utils.http import cookie_date
# from django.utils.http import http_date
# from django.utils.http import parse_http_date
# from django.utils.http import parse_etags
# from django.utils.http import quote_etag

# from django.utils.six.moves.urllib.parse import urlparse
# from django.utils.six.moves.urllib.parse import urlsplit
# from django.utils.six.moves.urllib.parse import urlunsplit


# from django.utils.module_loading import import_string
# from django.utils.module_loading import module_has_submodule


# from django.utils.text import capfirst
# from django.utils.text import get_text_list
# from django.utils.text import slugify


def index(request):
    return render(request, 'research_support/index.html')

def about(request):
    return render(request, 'research_support/about.html')

# def upload(request):
#     if request.method == 'POST':
#         form = UploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/pdfs/')
#     else:
#         form = UploadForm()
#     return render(request, 'research_support/upload.html', {
#         'form': form
#     })


def pdfs(request):
    pdfs = PDF.objects.all()
    return render(request, 'research_support/pdfs.html', {
        'pdfs': pdfs
    })

def pdf_detail(request, file_name): 
    pdf = PDF.objects.get(file_name=file_name)
    return render(request, 'research_support/pdf_detail.html', {
        'pdf': pdf
    })

def download_pdf(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    file_path = pdf.file_path
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response
    
    
# def analyze_pdf(request, file_name):
#     pdf = get_object_or_404(PDF, file_name=file_name)

#     # Interact with PDF Ai PDF API
#     # This is a simplified example. Replace with actual API endpoint and your API key
#     api_url = 'https://api.pdfaipdf.com/analyze'
#     api_key = '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' # Replace with your actual API key
#     files = {'file': (pdf.file_name, open(pdf.file_path, 'rb'))}
#     response = requests.post(api_url, headers={'API-Key': api_key}, files=files)

#     if response.status_code == 200:
#         analysis_results = response.json()
#         return render(request, 'analysis_results.html', {'pdf': pdf, 'results': analysis_results})
#     else:
#         # Handle errors or unsuccessful response
#         return render(request, 'analysis_error.html', {'pdf': pdf, 'error': response.text})

def analyze_pdf(request, pdf_id):
    pdf = get_object_or_404(PDF, pk=pdf_id)
    if request.method == 'POST':
        form = PDFAnalysisForm(request.POST)
        if form.is_valid():
            analysis_type = form.cleaned_data['analysis_type']
            # Call a function to perform the selected type of analysis
            results = perform_analysis(pdf, analysis_type)
            return render(request, 'analysis_results.html', {'pdf': pdf, 'results': results})
    else:
        form = PDFAnalysisForm()
    
    return render(request, 'select_analysis.html', {'form': form, 'pdf': pdf})

# Define a function to handle each type of analysis
def perform_analysis(pdf, analysis_type):
    # Depending on the analysis_type, interact with the PDF Ai PDF API
    # This is a placeholder. You'll need to implement actual API interaction based on the chosen analysis.
    pass


def perform_analysis(pdf, analysis_type):
    # Define the API endpoint and your API key
    api_url = 'https://api.pdfaipdf.com'  # Replace with the actual API endpoint
    api_key = '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'  # Replace with your actual API key

    # Prepare the file in the correct format for sending
    files = {'file': (pdf.file.name, pdf.file.open(), 'application/pdf')}
    
    # Depending on the analysis_type, set the specific endpoint
    if analysis_type == 'text_extraction':
        api_url += '/text_extraction'
    elif analysis_type == 'ocr':
        api_url += '/ocr'
    elif analysis_type == 'content_summarization':
        api_url += '/content_summarization'
    elif analysis_type == 'data_extraction':
        api_url += '/data_extraction'
    elif analysis_type == 'document_classification':
        api_url += '/document_classification'
    elif analysis_type == 'sentiment_analysis':
        api_url += '/sentiment_analysis'

    # Make the API request
    response = requests.post(api_url, headers={'API-Key': api_key}, files=files)

    # Close the file after sending
    pdf.file.close()

    # Check the response and return results or error
    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON data
    else:
        return {'error': response.text}
    
    

def chat_with_pdfs(request):
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            response = send_chat_request(message)
            return render(request, 'chat_response.html', {'response': response})
    else:
        form = ChatForm()

    return render(request, 'chat_with_pdfs.html', {'form': form})

def send_chat_request(message):
    api_url = 'https://pdf.ai/api/v1/chat-all'
    api_key = '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'  # Replace with your actual API key
    payload = {
        'message': message,
        'save_chat': True,  # or False, based on your requirement
        # Add other parameters as needed
    }
    headers = {'X-API-Key': api_key}
    
    response = requests.post(api_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Assuming the API returns a JSON response
    else:
        return {'error': 'Unable to process the request'}


def delete_pdf(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    pdf.delete()
    return HttpResponseRedirect('/pdfs/')

def edit_pdf(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = PDFForm(request.POST, request.FILES, instance=pdf)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = PDFForm(instance=pdf)
    return render(request, 'research_support/edit_pdf.html', {
        'form': form
    })

def update_pdf(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = PDFForm(request.POST, request.FILES, instance=pdf)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = PDFForm(instance=pdf)
    return render(request, 'research_support/update_pdf.html', {
        'form': form
    })


def upload_pdf(request):
    if request.method == 'POST':
        form = PDFForm(request.POST, request.FILES)
        if form.is_valid():
            new_pdf = form.save()
            # Redirect to the detail view of the newly uploaded PDF
            return HttpResponseRedirect(reverse('pdf_detail', args=[new_pdf.file_name]))
    else:
        form = PDFForm()
    return render(request, 'research_support/upload_pdf.html', {'form': form})

def upload_image(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            image = Image(document_id=pdf, image=image)
            image.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = ImageForm()
    return render(request, 'research_support/upload_image.html', {
        'form': form
    })

def delete_image(request, file_name, image_id):
    image = Image.objects.get(pk=image_id)
    image.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def download_image(request, file_name, image_id):

    image = Image.objects.get(pk=image_id)
    file_path = image.file_path
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="image/png")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response

def upload_summary(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = SummaryForm(request.POST)
        if form.is_valid():
            summary = form.cleaned_data['summary']
            summary = Summary(document_id=pdf, summary=summary)
            summary.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = SummaryForm()
    return render(request, 'research_support/upload_summary.html', {
        'form': form
    })

def delete_summary(request, file_name, summary_id):
    summary = Summary.objects.get(pk=summary_id)
    summary.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def upload_tag(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data['tag']
            tag = Tag(document_id=pdf, tag=tag)
            tag.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = TagForm()
    return render(request, 'research_support/upload_tag.html', {
        'form': form
    })

def delete_tag(request, file_name, tag_id):
    tag = Tag.objects.get(pk=tag_id)
    tag.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def upload_related(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = RelatedForm(request.POST)
        if form.is_valid():
            related_document_id = form.cleaned_data['related_document_id']
            related = Related(document_id=pdf, related_document_id=related_document_id)
            related.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = RelatedForm()
    return render(request, 'research_support/upload_related.html', {
        'form': form
    })

def delete_related(request, file_name, related_id):
    related = Related.objects.get(pk=related_id)
    related.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def upload_vector(request, file_name):


    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = VectorForm(request.POST)
        if form.is_valid():
            vector = form.cleaned_data['vector']
            vector = Vector(document_id=pdf, vector=vector)
            vector.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = VectorForm()
    return render(request, 'research_support/upload_vector.html', {
        'form': form
    })

def delete_vector(request, file_name, vector_id):
    vector = Vector.objects.get(pk=vector_id)
    vector.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def upload_qa(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = QAForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            answer = form.cleaned_data['answer']
            qa = QA(document_id=pdf, question=question, answer=answer)
            qa.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = QAForm()
    return render(request, 'research_support/upload_qa.html', {
        'form': form
    })

def delete_qa(request, file_name, qa_id):

    qa = QA.objects.get(pk=qa_id)
    qa.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def upload_feedback(request, file_name):

    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.cleaned_data['feedback']
            feedback = Feedback(document_id=pdf, feedback=feedback)
            feedback.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = FeedbackForm()
    return render(request, 'research_support/upload_feedback.html', {
        'form': form
    })

def delete_feedback(request, file_name, feedback_id):
    feedback = Feedback.objects.get(pk=feedback_id)
    feedback.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def upload_query(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            query = Query(document_id=pdf, query=query)
            query.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = QueryForm()
    return render(request, 'research_support/upload_query.html', {
        'form': form
    })

def delete_query(request, file_name, query_id):
    query = Query.objects.get(pk=query_id)
    query.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))


    
def search(request):
    form = SearchForm()
    return render(request, 'research_support/search.html', {
        'form': form
    })

def search_results(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
            pdfs = PDF.objects.filter(Q(file_name__icontains=search_query) | Q(text_content__icontains=search_query))
            return render(request, 'research_support/search_results.html', {
                'pdfs': pdfs
            })
        else:
            return HttpResponseRedirect('/search/')
    else:
        return HttpResponseRedirect('/search/')

def feedback(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.cleaned_data['feedback']
            feedback = Feedback(document_id=pdf, feedback=feedback)
            feedback.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = FeedbackForm()
    return render(request, 'research_support/feedback.html', {
        'form': form
    })

def delete_feedback(request, file_name, feedback_id):

    feedback = Feedback.objects.get(pk=feedback_id)
    feedback.delete()
    return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def query(request, file_name):

    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            query = Query(document_id=pdf, query=query)
            query.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = QueryForm()
    return render(request, 'research_support/query.html', {
        'form': form
    })

def delete_query(request, file_name, query_id):
    
        query = Query.objects.get(pk=query_id)
        query.delete()
        return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def summary(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = SummaryForm(request.POST)
        if form.is_valid():
            summary = form.cleaned_data['summary']
            summary = Summary(document_id=pdf, summary=summary)
            summary.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = SummaryForm()
    return render(request, 'research_support/summary.html', {
        'form': form
    })

def delete_summary(request, file_name, summary_id):
        
            summary = Summary.objects.get(pk=summary_id)
            summary.delete()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def tag(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data['tag']
            tag = Tag(document_id=pdf, tag=tag)
            tag.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = TagForm()
    return render(request, 'research_support/tag.html', {
        'form': form
    })

def delete_tag(request, file_name, tag_id):
        
            tag = Tag.objects.get(pk=tag_id)
            tag.delete()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def related(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = RelatedForm(request.POST)
        if form.is_valid():
            related_document_id = form.cleaned_data['related_document_id']
            related = Related(document_id=pdf, related_document_id=related_document_id)
            related.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = RelatedForm()
    return render(request, 'research_support/related.html', {
        'form': form
    })

def delete_related(request, file_name, related_id):
        
            related = Related.objects.get(pk=related_id)
            related.delete()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def vector(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = VectorForm(request.POST)
        if form.is_valid():
            vector = form.cleaned_data['vector']
            vector = Vector(document_id=pdf, vector=vector)
            vector.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = VectorForm()
    return render(request, 'research_support/vector.html', {
        'form': form
    })

def delete_vector(request, file_name, vector_id):
        
            vector = Vector.objects.get(pk=vector_id)
            vector.delete()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def qa(request, file_name):

    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = QAForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            answer = form.cleaned_data['answer']
            qa = QA(document_id=pdf, question=question, answer=answer)
            qa.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = QAForm()
    return render(request, 'research_support/qa.html', {
        'form': form
    })

def delete_qa(request, file_name, qa_id):
        
            qa = QA.objects.get(pk=qa_id)
            qa.delete()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def image(request, file_name):

    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            image = Image(document_id=pdf, image=image)
            image.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = ImageForm()
    return render(request, 'research_support/image.html', {
        'form': form
    })

def delete_image(request, file_name, image_id):
        
            image = Image.objects.get(pk=image_id)
            image.delete()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def document(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.pdf = pdf
            document.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = DocumentForm()
    return render(request, 'research_support/document.html', {
        'form': form
    })

def delete_document(request, file_name, document_id):
        
            document = Document.objects.get(pk=document_id)
            document.delete()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))

def download_document(request, file_name, document_id):


    document = Document.objects.get(pk=document_id)
    file_path = document.file_path
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response

def view_document(request, file_name, document_id):
    document = Document.objects.get(pk=document_id)
    return render(request, 'research_support/view_document.html', {
        'document': document
    })

def edit_document(request, file_name, document_id):

    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = DocumentForm(instance=document)
    return render(request, 'research_support/edit_document.html', {
        'form': form
    })

def update_document(request, file_name, document_id):

    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = DocumentForm(instance=document)
    return render(request, 'research_support/update_document.html', {
        'form': form
    })

def upload_document(request, file_name, document_id):

    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = DocumentForm(instance=document)
    return render(request, 'research_support/upload_document.html', {
        'form': form
    })

def upload_image(request, file_name, document_id):

    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            image = Image(document_id=document, image=image)
            image.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = ImageForm()
    return render(request, 'research_support/upload_image.html', {
        'form': form
    })

def upload_summary(request, file_name, document_id):

    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = SummaryForm(request.POST)
        if form.is_valid():
            summary = form.cleaned_data['summary']
            summary = Summary(document_id=document, summary=summary)
            summary.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = SummaryForm()
    return render(request, 'research_support/upload_summary.html', {
        'form': form
    })

def upload_tag(request, file_name, document_id):

    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data['tag']
            tag = Tag(document_id=document, tag=tag)
            tag.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = TagForm()
    return render(request, 'research_support/upload_tag.html', {
        'form': form
    })

def upload_related(request, file_name, document_id):

    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = RelatedForm(request.POST)
        if form.is_valid():
            related_document_id = form.cleaned_data['related_document_id']
            related = Related(document_id=document, related_document_id=related_document_id)
            related.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = RelatedForm()
    return render(request, 'research_support/upload_related.html', {
        'form': form
    })

def upload_vector(request, file_name, document_id):
         
        document = Document.objects.get(pk=document_id)
        if request.method == 'POST':
            form = VectorForm(request.POST)
            if form.is_valid():
                vector = form.cleaned_data['vector']
                vector = Vector(document_id=document, vector=vector)
                vector.save()
                return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
        else:
            form = VectorForm()
        return render(request, 'research_support/upload_vector.html', {
            'form': form
        })

def upload_qa(request, file_name, document_id):

    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = QAForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            answer = form.cleaned_data['answer']
            qa = QA(document_id=document, question=question, answer=answer)
            qa.save()
            return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
    else:
        form = QAForm()
    return render(request, 'research_support/upload_qa.html', {
        'form': form
    })

def upload_feedback(request, file_name, document_id):
         
        document = Document.objects.get(pk=document_id)
        if request.method == 'POST':
            form = FeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.cleaned_data['feedback']
                feedback = Feedback(document_id=document, feedback=feedback)
                feedback.save()
                return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
        else:
            form = FeedbackForm()
        return render(request, 'research_support/upload_feedback.html', {
            'form': form
        })

def upload_query(request, file_name, document_id):
            
        document = Document.objects.get(pk=document_id)
        if request.method == 'POST':
            form = QueryForm(request.POST)
            if form.is_valid():
                query = form.cleaned_data['query']
                query = Query(document_id=document, query=query)
                query.save()
                return HttpResponseRedirect(reverse('pdf_detail', args=[file_name]))
        else:
            form = QueryForm()
        return render(request, 'research_support/upload_query.html', {
            'form': form
        })
