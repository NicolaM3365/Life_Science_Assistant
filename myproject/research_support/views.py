import os
import requests
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
import logging


from .models import PDF, Document, Image, Summary, Tag, Related, Vector, QA, Feedback, Query
from .forms import (
    DocumentForm, ImageForm, SummaryForm, TagForm, RelatedForm, VectorForm,
    QAForm, FeedbackForm, QueryForm, SearchForm, UploadForm, PDFForm,
    ChatForm, PDFAnalysisForm, UploadPDFUrlForm, UploadPDFForm
)

# Set up logging (you can configure it more appropriately for your project)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def handle_upload_response(request, upload_type, response):
    if response.status_code == 200:
        # Handle successful upload
        # You can redirect to a success page or another appropriate page
        return HttpResponseRedirect(reverse('success_url'))

    elif response.status_code == 400:
        # Handle bad request errors
        # You can render an error page or pass error information to the template
        error_message = "Bad request error: {}".format(response.text)
        return HttpResponseServerError(error_message)

    elif response.status_code == 404:
        # Handle not found errors
        # You can render an error page or pass error information to the template
        error_message = "Not found error: {}".format(response.text)
        return HttpResponseServerError(error_message)

    elif response.status_code == 413:
        # Handle file size exceeded errors for file upload
        if upload_type == 'file':
            error_message = "File size exceeds the limit (4.5 MB). Please upload a smaller file or use the URL upload method."
            return HttpResponseServerError(error_message)
        else:
            error_message = "Request Entity Too Large: {}".format(response.text)
            return HttpResponseServerError(error_message)

    elif response.status_code == 504:
        # Handle timeout errors
        error_message = "Timeout error: The upload process took too long (300 seconds). Please try again later or use a different upload method."
        return HttpResponseServerError(error_message)

    else:
        # Handle other errors
        error_message = "An error occurred during the upload: {}".format(response.text)
        return HttpResponseServerError(error_message)

def success_page(request):
    return render(request, 'research_support/success.html')
    
def my_view(request):
    api_key = os.environ.get('PDF_AI_API_KEY')
    if not api_key:
        raise ValueError("No API key set for PDF Ai PDF")
    # Use the api_key in your API calls
    # ... rest of your view logic ...


def index(request):
    return render(request, 'research_support/index.html')

def about(request):
    return render(request, 'research_support/about.html')


def pdfs(request):
    pdfs = PDF.objects.all()
    return render(request, 'research_support/pdfs.html', {'pdfs': pdfs})

def pdf_detail(request, file_name): 
    pdf = PDF.objects.get(file_name=file_name)
    return render(request, 'research_support/pdf_detail.html', {'pdf': pdf})

def download_pdf(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    file_path = pdf.file_path
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response

# Add other view functions here

# For example: upload_pdf, upload_image, delete_pdf, etc.

# Make sure to add all the necessary view functions you need for your application.

def delete_pdf(request, file_name):
    pdf = PDF.objects.get(file_name=file_name)
    pdf.delete()
    return HttpResponseRedirect('pdfs/')

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = PDF.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
            return render(request, 'research_support/search_results.html', {'results': results, 'query': query})
    else:
        form = SearchForm()
    return render(request, 'research_support/search.html', {'form': form})


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
        # Check which form is being submitted
        if 'url_submit' in request.POST:
            url_form = UploadPDFUrlForm(request.POST)
            file_form = UploadPDFForm()
            if url_form.is_valid():
                # Handle URL upload
                logger.debug(f"Request.FILES content: {request.FILES}")
                response = upload_pdf_to_ai_pdf_api(url_form.cleaned_data, upload_type='url')
                return handle_upload_response(response, request)
        elif 'file_submit' in request.POST:
            file_form = UploadPDFForm(request.POST, request.FILES)
            url_form = UploadPDFUrlForm()
            if file_form.is_valid():
                if 'file' in request.FILES:
                    logger.info("File is present in the request.")
                # Handle file upload
                response = upload_pdf_to_ai_pdf_api(file_form.cleaned_data, upload_type='file')
                return handle_upload_response(response, request)
    else:
        url_form = UploadPDFUrlForm()
        file_form = UploadPDFForm()


    # If the request method is not POST or form submission is not valid, render the form
    logger.debug(f"Request.FILES: {request.FILES}")
    return render(request, 'research_support/upload_pdf.html', {'url_form': url_form, 'file_form': file_form})

def upload_pdf_to_ai_pdf_api(data, upload_type):
    api_url = 'https://pdf.ai/api/v1/upload/'
    api_url += 'url' if upload_type == 'url' else 'file'
    api_key = os.environ.get('PDF_AI_API_KEY')

    if not api_key:
        raise ValueError("No API key set for PDF Ai PDF")
    
    headers = {'X-API-Key': api_key}
     # Initialize the variables to ensure they are defined
    form_data = {}
    files = {}
    
    if upload_type == 'url':
        payload = {'url': data['url'], 'isPrivate': data.get('isPrivate', False), 'ocr': data.get('ocr', False)}
        response = requests.post(api_url, json=payload, headers=headers)
    else:  # upload_type == 'file'
        files = {'file': data['file']}
        form_data = {'isPrivate': data.get('isPrivate', False), 'ocr': data.get('ocr', False)}
        logger.info(f"File name: {data['file'].name}, File size: {data['file'].size}")
        response = requests.post(api_url, files=files, data=form_data, headers=headers)

    logger.debug(f"Form data being sent: {form_data}")
    logger.debug(f"Files being sent: {files}")
    
    return response

def upload_error(request):
    # The error handling logic goes here (you might want to customize this)
    # Since this view might not be directly called with context, you may want to handle no context case.
    error_message = request.GET.get('error', 'An unknown error occurred.')
    return render(request, 'research_support/upload_error.html', {'error': error_message})




def handle_upload_response(response, request):
    if response.status_code == 200:
        # Handle successful upload
        # You can redirect to a success page or another appropriate page
        return HttpResponseRedirect('success/')
        
    else:
        # Log or print the response for debugging
        logger.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")
        # You can also use print for quick debugging (not recommended for production)
        # print(f"Upload failed. Status Code: {response.status_code}. Response: {response.text}")

        # Use render to display the error page along with the error message
        return render(request, 'research_support/upload_error.html', {'error': response.text})


def chat_with_pdfs(request):
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            response = send_chat_request(message)
            return render(request, 'research_support/chat_response.html', {'response': response})
    else:
        form = ChatForm()

    return render(request, 'research_support/chat_with_pdfs.html', {'form': form})

def send_chat_request(message):
    api_url = 'https://pdf.ai/api/v1/chat-all'
    api_key = os.environ.get('PDF_AI_API_KEY')

    if not api_key:
        raise ValueError("No API key set for PDF Ai PDF")

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


