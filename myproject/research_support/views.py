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


# def pdfs(request):
#     pdfs = PDF.objects.all()
#     return render(request, 'research_support/pdfs.html', {'pdfs': pdfs})

# def pdf_detail(request, file_name): 
#     pdf = PDF.objects.get(file_name=file_name)
#     return render(request, 'research_support/pdf_detail.html', {'pdf': pdf})

def download_pdf(request, doc_id):
    pdf = PDF.objects.get(doc_id=doc_id)
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
    return redirect('research_support:get_all_pdfs')

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


# def edit_pdf(request, doc_id):
#     pdf = PDF.objects.get(doc_id=doc_id)
#     if request.method == 'POST':
#         form = PDFForm(request.POST, request.FILES, instance=pdf)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('research_support:pdf_detail', args=[doc_id]))
#     else:
#         form = PDFForm(instance=pdf)
#     return render(request, 'research_support/edit_pdf.html', {'form': form})

def update_pdf(request, doc_id):
    pdf = PDF.objects.get(doc_id=doc_id)
    if request.method == 'POST':
        form = PDFForm(request.POST, request.FILES, instance=pdf)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('research_support:pdf_detail', args=[doc_id]))
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
            # Adjusted endpoint for URL upload
            url_endpoint = api_url + 'url'
            payload = {'url': data.get('url'), 'isPrivate': data.get('isPrivate', False), 'ocr': data.get('ocr', False)}
            response = requests.post(url_endpoint, json=payload, headers=headers)
        elif upload_type == 'file':
            # Adjusted endpoint for file upload
            file_endpoint = api_url + 'file'
            file_obj = data.get('file')
            if file_obj:
                files = {'file': (file_obj.name, file_obj, 'application/pdf')}
                form_data = {'isPrivate': data.get('isPrivate', False), 'ocr': data.get('ocr', False)}
                response = requests.post(file_endpoint, files=files, data=form_data, headers=headers)
                logger.info(f"File name: {file_obj.name}, File size: {file_obj.size}")
            else:
                logger.error("File object not found in data")
                return None
            
            # Handle the response from the API

# Assuming this snippet is part of the function that handles the upload and receives the response

            if response and response.status_code == 200:
                response_data = response.json()
                logger.debug(f"API Response: {response_data}")  # Detailed logging of the response

                doc_id = response_data.get('docId')
                if doc_id:
                    logger.info(f"Document uploaded successfully. Document ID: {doc_id}")
                    # Assuming the function returns here, indicating success
                    return response_data
                else:
                    logger.error("docId not found in the API response.")
                    # Handle the absence of docId appropriately
            else:
                logger.error(f"Upload failed. Status code: {response.status_code}, Response: {response.text}")
                # Handle failure scenario appropriately

            

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
        return render(request, 'research_support/get_all_pdfs_error.html', {'error': pdfs['error']})
    else:
        # Render the PDFs using the template
        return render(request, 'research_support/get_all_pdfs.html', {'pdfs': pdfs})

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



# Django view function to display the details of a specific PDF document
def get_pdf(request, doc_id):
    if not doc_id:
        # Handle the case where doc_id is empty or not provided
        return HttpResponse("Document ID is required.", status=400)

    api_key = os.environ.get('PDF_AI_API_KEY')
    if not api_key:
        # Provide a user-friendly error message if the API key is missing
        return HttpResponse("API key for PDF.AI is not configured properly in the environment variables.", status=500)
    
    pdf_detail = get_pdf_from_ai_pdf_api(api_key, doc_id)
    if 'error' in pdf_detail:
        # Render an error template if there was an issue fetching the document
        return render(request, 'research_support/get_pdf_error.html', {'error': pdf_detail['error']})
    
    # Check if 'id' is present in the response; if not, it indicates an unexpected issue
    if 'id' not in pdf_detail:
        return render(request, 'research_support/get_pdf_error.html', {'error': 'No document ID found in the API response.'})

    # Render a template to display the PDF details, assuming 'pdf_detail.html' is set up for this purpose
    return render(request, 'research_support/pdf_detail.html', {'pdf': pdf_detail, 'doc_id': pdf_detail.get('id', doc_id)}) # Fallback to doc_id if 'id' isn't present in the response

def get_pdf_from_ai_pdf_api(api_key, doc_id):
    # Construct the request URL using the document ID
    url = f"https://pdf.ai/api/v1/documents/{doc_id}"
    headers = {"X-API-KEY": api_key}
    
    # Make the GET request to the API
    response = requests.get(url, headers=headers)
    
    # Check the response status code
    if response.status_code == 200:
        pdf_detail = response.json()
        doc_id = pdf_detail.get('id', 'No ID found in response')
        # Assuming the API response includes 'id' as the document's unique identifier
        return pdf_detail   
    else:
        # Log or handle errors as appropriate
        print(f"Error fetching document {doc_id}: {response.status_code}")
        return {"error": f"Failed to get document {doc_id}, status code: {response.status_code}"}

def chat_with_pdf(request):
    doc_id = request.session.get('id')
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            response = send_chat_request(message,doc_id)
            return render(request, 'research_support/chat_response.html', {'response': response})
    else:
        form = ChatForm()

    return render(request, 'research_support/chat_with_pdf.html', {'form': form})

def send_chat_request(message, doc_id): 
    api_url = 'https://pdf.ai/api/v1/chat'
    api_key = os.environ.get('PDF_AI_API_KEY')
    if  not api_key:
        raise ValueError("No API key set for PDF Ai PDF")       

    payload = {
        'id': doc_id, # Replace with the actual document ID
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
        return {'error': 'Bad request - missing API key, id, or message'}
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

def summarize_pdf(request):
    form = SummaryForm(request.POST or None)
    summary_result = None
    error_message = None

    if request.method == 'POST' and form.is_valid():
        api_key = os.environ.get('PDF_AI_API_KEY')
        if not api_key:
            error_message = "API key not found. Please set the PDF_AI_API_KEY environment variable."
        else:
            doc_id = form.cleaned_data.get('document_id')
            language = form.cleaned_data.get('language', None)  # Assuming you add a 'language' field to your form

            # Make the API request to summarize the PDF
            url = "https://pdf.ai/api/v1/summary"
            headers = {"X-API-Key": api_key}
            payload = {"docId": doc_id, "language": language}
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                summary_result = response.json().get('content')

                # Log the entire API response for debugging
                logger.debug(f"API response: {response_data}")
    
                # Here you can also save the summary to your database if needed
                # logger.debug(f"API response: {response.json()} Status Code: {response.status_code}")

            else:
                error_message = f"Failed to summarize document, status code: {response.status_code}"
                # Log detailed error information
                logger.error(f"API response error. Status Code: {response.status_code}, Response: {response.text}")

    return render(request, 'research_support/summarize_pdf.html', {'form': form, 'summary_result': summary_result, 'error': error_message})
      


def delete_pdf(request, doc_id):
    api_key = 'Your_MyAIDrive_API_Key'  # Ideally, fetch this from a secure place like environment variables
    result = delete_pdf_from_ai_pdf_api(api_key, doc_id)

    if "message" in result:
        # If the API returned a success message, redirect to a success page or the list of PDFs
        messages.success(request, result["message"])
        return redirect('research_support:get_all_pdfs')  # Replace 'pdfs_list_url' with the name of your URL to list PDFs
    else:
        # If there was an error, display the error message to the user
        error_message = result.get("error", "An unknown error occurred.")
        messages.error(request, error_message)
        return redirect('research_support:get_all_pdfs')  # You might redirect back to where the user was, or to an error page




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



# def upload_pdf_and_get_doc_id(request):
#     if request.method == 'POST':
#         # Initialize forms regardless of submission to avoid UnboundLocalError
#         url_form = UploadPDFUrlForm()
#         file_form = UploadPDFForm()

#         if 'url_submit' in request.POST:
#             url_form = UploadPDFUrlForm(request.POST)
#             if url_form.is_valid():
#                 # Process URL upload and API call
#                 response = upload_pdf_to_ai_pdf_api(url_form.cleaned_data, upload_type='url')
#                 return handle_upload_response(response, request)
#         elif 'file_submit' in request.POST:
#             file_form = UploadPDFForm(request.POST, request.FILES)
#             if file_form.is_valid() and 'file' in request.FILES:
#                 # Process file upload and API call
#                 logger.info("File is present in the request.")
#                 response = upload_pdf_to_ai_pdf_api(file_form.cleaned_data, upload_type='file')
#                 return handle_upload_response(response, request)
#     else:
#         # Initialize forms for GET request
#         url_form = UploadPDFUrlForm()
#         file_form = UploadPDFForm()

#     # Log debug information
#     logger.debug(f"Request.FILES: {request.FILES}")
#     # Render the upload forms
#     return render(request, 'research_support/upload_pdf.html', {'url_form': url_form, 'file_form': file_form})

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
    
def handle_summary_response(response, request):
    # Assuming the response is a dictionary that may contain 'error' or the summary content
    if "error" in response:
        # Log the error and render an error message on the summary page
        logger.error(f"Summary retrieval failed with error: {response['error']}")
        return render(request, 'research_support/summarize_pdf.html', {'error': response['error']})
    
    elif "content" in response:
        # Extract the summary content from the response
        summary_content = response.get('content')
        # Render a template showing the summary content
        return render(request, 'research_support/summary_response.html', {'summary_content': summary_content})
    
    else:
        # Handle unexpected response format
        logger.error("Unexpected response format received from summary function")
        return render(request, 'research_support/summarize_pdf.html', {'error': 'Unexpected error occurred. Please try again.'})
