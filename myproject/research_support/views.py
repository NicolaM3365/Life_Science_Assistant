import os
import requests
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
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


# def handle_upload_response(request, upload_type, response):
#     if response.status_code == 200:
#         # Handle successful upload
#         # You can redirect to a success page or another appropriate page
#         return HttpResponseRedirect(reverse('success_url'))

#     elif response.status_code == 400:
#         # Handle bad request errors
#         # You can render an error page or pass error information to the template
#         error_message = "Bad request error: {}".format(response.text)
#         return HttpResponseServerError(error_message)

#     elif response.status_code == 404:
#         # Handle not found errors
#         # You can render an error page or pass error information to the template
#         error_message = "Not found error: {}".format(response.text)
#         return HttpResponseServerError(error_message)

#     elif response.status_code == 413:
#         # Handle file size exceeded errors for file upload
#         if upload_type == 'file':
#             error_message = "File size exceeds the limit (4.5 MB). Please upload a smaller file or use the URL upload method."
#             return HttpResponseServerError(error_message)
#         else:
#             error_message = "Request Entity Too Large: {}".format(response.text)
#             return HttpResponseServerError(error_message)

#     elif response.status_code == 504:
#         # Handle timeout errors
#         error_message = "Timeout error: The upload process took too long (300 seconds). Please try again later or use a different upload method."
#         return HttpResponseServerError(error_message)

#     else:
#         # Handle other errors
#         error_message = "An error occurred during the upload: {}".format(response.text)
#         return HttpResponseServerError(error_message)

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


def pdf_options(request, doc_id):
    # Store doc_id in the session
    request.session['doc_id'] = doc_id
    # Render a template that offers buttons/links to chat or summarize the PDF
    return render(request, 'research_support/pdf_options.html', {'doc_id': doc_id})



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
    api_key = os.environ.get('PDF_AI_API_KEY')

    if not api_key:
        raise ValueError("No API key set for PDF Ai PDF")

    headers = {'X-API-Key': api_key}
    

    try:
        response = None
        if upload_type == 'url':
            payload = {'url': data.get('url'), 'isPrivate': data.get('isPrivate', False), 'ocr': data.get('ocr', False)}
            response = requests.post(api_url + 'url', json=payload, headers=headers)
        elif upload_type == 'file':
            file_obj = data.get('file')
            if file_obj:
                files = {'file': (file_obj.name, file_obj, 'application/pdf')}
                form_data = {'isPrivate': data.get('isPrivate', False), 'ocr': data.get('ocr', False)}
                response = requests.post(api_url + 'file', files=files, data=form_data, headers=headers)
                logger.info(f"File name: {file_obj.name}, File size: {file_obj.size}")
            else:
                logger.error("File object not found in data")
                return None
            
            # Handle the response from the API
        if response and response.status_code == 200:
            response_data = response.json()
            # Log success and return the whole response
            # Modify the below if you're looking for a specific key in the response JSON
            document_id = response_data.get('document_id', 'No ID found in response')  # Example key extraction
            logger.info(f"Document uploaded successfully. Document ID: {document_id}")
            return response_data  # Return the full response data or just the document ID as needed
        else:
            # Log detailed error information
            if response:
                logger.error(f"Failed to upload PDF. Status code: {response.status_code}. Response: {response.text}")
            else:
                logger.error("Failed to upload PDF. No response from server.")
            return None

    except requests.exceptions.RequestException as e:
        # Log request errors
        logger.error(f"Request to PDF AI API failed: {e}")
        return None

def upload_error(request):
    # The error handling logic goes here (you might want to customize this)
    # Since this view might not be directly called with context, you may want to handle no context case.
    error_message = request.GET.get('error', 'An unknown error occurred.')
    return render(request, 'research_support/upload_error.html', {'error': error_message})




# def handle_upload_response(response, request):
#     if response.status_code == 200:
#         # Handle successful upload
#         # You can redirect to a success page or another appropriate page
#         return HttpResponseRedirect('success/')
        
#     else:
#         # Log or print the response for debugging
#         logger.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")
#         # You can also use print for quick debugging (not recommended for production)
#         # print(f"Upload failed. Status Code: {response.status_code}. Response: {response.text}")

#         # Use render to display the error page along with the error message
#         return render(request, 'research_support/upload_error.html', {'error': response.text})

def get_all_pdfs(request):
    api_key = os.environ.get('PDF_AI_API_KEY')
    if not api_key:
        return HttpResponse("API key for PDF.AI is not configured properly in the environment variables.", status=500)
        # raise ValueError("No API key set for PDF Ai PDF")   
    pdfs = get_all_pdfs_from_ai_pdf_api(api_key)
    
    # Check if the response from the helper function contains an error
    if 'error' in pdfs:
        # Pass the error message to the template for user-friendly feedback
        return render(request, 'research_support/error.html', {'error': pdfs['error']})
    else:
        # Render the PDFs using the template
        return render(request, 'research_support/pdfs.html', {'pdfs': pdfs})

def get_all_pdfs_from_ai_pdf_api(api_key):
    url = "https://pdf.ai/api/v1/documents"
    headers = {
        "X-API-KEY":api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json() ['data']
    else:
        print(f"Error fetching documents: {response.status_code}")
        return {"error": f"Failed to get documents, status code: {response.status_code}"}


def get_pdf_from_ai_pdf_api(api_key, doc_id):
    # Construct the request URL using the document ID
    url = f"https://pdf.ai/api/v1/documents/{doc_id}"
    headers = {"X-API-KEY": api_key}
    
    # Make the GET request to the API
    response = requests.get(url, headers=headers)
    
    # Check the response status code
    if response.status_code == 200:
        # Return the document's details if the request was successful
        return response.json()
    else:
        # Log or handle errors as appropriate
        print(f"Error fetching document {doc_id}: {response.status_code}")
        return {"error": f"Failed to get document {doc_id}, status code: {response.status_code}"}

# Django view function to display the details of a specific PDF document
def get_pdf(request, doc_id):
    api_key = os.environ.get('PDF_AI_API_KEY')
    if not api_key:
        # Provide a user-friendly error message if the API key is missing
        return HttpResponse("API key for PDF.AI is not configured properly in the environment variables.", status=500)
    
    pdf_details = get_pdf_from_ai_pdf_api(api_key, doc_id)
    if 'error' in pdf_details:
        # Render an error template if there was an issue fetching the document
        return render(request, 'research_support/error.html', {'error': pdf_details['error']})
    
    # Render a template to display the PDF details, assuming 'pdf_detail.html' is set up for this purpose
    return render(request, 'research_support/pdf_detail.html', {'pdf': pdf_details})

def chat_with_pdf(request):
    doc_id = request.session.get('doc_id')
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            response = send_chat_request(message)
            return render(request, 'research_support/chat_response.html', {'response': response})
    else:
        form = ChatForm()

    return render(request, 'research_support/chat_with_pdfs.html', {'form': form})

def send_chat_request(message, doc_id): 
    api_url = 'https://pdf.ai/api/v1/chat'
    api_key = os.environ.get('PDF_AI_API_KEY')
    if  not api_key:
        raise ValueError("No API key set for PDF Ai PDF")       

    payload = {
        'doc_id': doc_id, # Replace with the actual document ID
        'message': message,
        'save_chat': True, # or False, based on your requirement
        # Add other parameters as needed
        'use_gpt4': True, # or False, based on your requirement
        'language': 'en', # or 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru', 'ja', 'ko', 'zh', 'ar', 'tr', 'he', 'id', 'th', 'vi', 'hi', 'bn', 'fa', 'ur', 'ms', 'fil', 'ta', 'te', 'ml', 'kn', 'mr', 'gu', 'pa', 'si', 'my', 'km', 'lo', 'ne
    }
    headers = {'X-API-Key': api_key}    
    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        return {'error': 'Invalid API key'}
    elif response.status_code == 400:
        return {'error': 'Bad request - missing API key, docId, or message'}
    else:
        return {'error': f'Unable to process the request. Status code: {response.status_code}'}


def send_chat_all_request(message):
    api_url = 'https://pdf.ai/api/v1/chat-all/'
    api_key = os.environ.get('PDF_AI_API_KEY')
    if not api_key:
        raise ValueError("No API key set for PDF Ai PDF")
    payload = {
        'message': message,
        'save_chat': True,  # or False, based on your requirement
        # Add other parameters as needed
        'use_gpt4': True,  # or False, based on your requirement
        'language': 'en',  # or 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru', 'ja', 'ko', 'zh', 'ar', 'tr', 'he', 'id', 'th', 'vi', 'hi', 'bn', 'fa', 'ur', 'ms', 'fil', 'ta', 'te', 'ml', 'kn', 'mr', 'gu', 'pa', 'si', 'my', 'km', 'lo', 'ne
    }
    headers = {'X-API-Key': api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Unable to process the request'}
       
    

def send_summary_request(api_key, doc_id, language=None):
    url = "https://pdf.ai/api/v1/summary"
    headers = {
        "X-API-Key":api_key
    }
    payload = {
        "docId": doc_id,
    }
     # Optionally add the language to the payload if specified
    if language:
        payload['language'] = language

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json() ['data']
    else:
        return {"error": f"Failed to summarize document, status code: {response.status_code}"}

def summarize_pdf(request):
    api_key = os.environ.get('PDF_AI_API_KEY')  # Get the API key from environment variables
    if not api_key:
        raise ValueError("API key not found. Please set the PDF_AI_API_KEY environment variable.")

    if request.method == 'POST':
        form = SummaryForm(request.POST)
        if form.is_valid():
            doc_id = form.cleaned_data['doc_id']
            language = form.cleaned_data.get('language', None)  # Assuming your form has a language field
            
            response = send_summary_request(api_key, doc_id, language)
            
            if response.get('error'):
                return render(request, 'research_support/summarize_pdf.html', {'form': form, 'error': response['error']})
            else:
                return render(request, 'research_support/summary_response.html', {'response': response})
    else:
        form = SummaryForm()
    
    return render(request, 'research_support/summarize_pdf.html', {'form': form})

def delete_pdf(request, doc_id):
    api_key = 'Your_MyAIDrive_API_Key'  # Ideally, fetch this from a secure place like environment variables
    result = delete_pdf_from_ai_pdf_api(api_key, doc_id)

    if "message" in result:
        # If the API returned a success message, redirect to a success page or the list of PDFs
        messages.success(request, result["message"])
        return redirect('pdfs_list_url')  # Replace 'pdfs_list_url' with the name of your URL to list PDFs
    else:
        # If there was an error, display the error message to the user
        error_message = result.get("error", "An unknown error occurred.")
        messages.error(request, error_message)
        return redirect('pdfs_list_url')  # You might redirect back to where the user was, or to an error page




def delete_pdf_from_ai_pdf_api(api_key, doc_id):
    url = f"https://pdf.ai/api/v1/documents/{doc_id}"
    headers = {
        "X-API-KEY":api_key
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        return response.json() ['data']
    else:
        return {"error": f"Failed to delete document, status code: {response.status_code}"}



def upload_pdf_and_get_doc_id(request):
    if request.method == 'POST':
        # Initialize forms regardless of submission to avoid UnboundLocalError
        url_form = UploadPDFUrlForm()
        file_form = UploadPDFForm()

        if 'url_submit' in request.POST:
            url_form = UploadPDFUrlForm(request.POST)
            if url_form.is_valid():
                # Process URL upload and API call
                response = upload_pdf_to_ai_pdf_api(url_form.cleaned_data, upload_type='url')
                return handle_upload_response(response, request)
        elif 'file_submit' in request.POST:
            file_form = UploadPDFForm(request.POST, request.FILES)
            if file_form.is_valid() and 'file' in request.FILES:
                # Process file upload and API call
                logger.info("File is present in the request.")
                response = upload_pdf_to_ai_pdf_api(file_form.cleaned_data, upload_type='file')
                return handle_upload_response(response, request)
    else:
        # Initialize forms for GET request
        url_form = UploadPDFUrlForm()
        file_form = UploadPDFForm()

    # Log debug information
    logger.debug(f"Request.FILES: {request.FILES}")
    # Render the upload forms
    return render(request, 'research_support/upload_pdf.html', {'url_form': url_form, 'file_form': file_form})

def handle_upload_response(response, request):
    # Check if response is a dictionary and contains an error key
    if isinstance(response, dict) and "error" in response:
        # Log the error and render the error template
        logger.error(f"Upload failed with error: {response['error']}")
        return render(request, 'research_support/upload_error.html', {'error': 'Failed to upload PDF. Please try again.'})
    
    # If the response is a dictionary but does not contain an "error" key, it's assumed to be successful
    elif isinstance(response, dict) and "docId" in response:
        # Extract document ID from response
        doc_id = response.get('docId')
        # Render success template with doc_id
        return render(request, 'research_support/upload_success.html', {'doc_id': doc_id})
    
    else:
        # Handle unexpected response format
        logger.error("Unexpected response format received from upload function")
        return render(request, 'research_support/upload_error.html', {'error': 'Unexpected error occurred. Please try again.'})