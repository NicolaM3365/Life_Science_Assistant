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
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import logging


from .models import PDF, Document, Image, Summary, Tag, Related, Vector, QA, Feedback, Query
from .forms import (
    DocumentForm, ImageForm, SummaryForm, TagForm, RelatedForm, VectorForm,
    QAForm, FeedbackForm, QueryForm, SearchForm, UploadForm, PDFForm,
    ChatForm, PDFAnalysisForm, UploadPDFUrlForm, UploadPDFForm, DeletePDFForm
)

# Set up logging (you can configure it more appropriately for your project)
logger = logging.getLogger("research_support.views")


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



def upload_error(request):
    # The error handling logic goes here (you might want to customize this)
    # Since this view might not be directly called with context, you may want to handle no context case.
    error_message = request.GET.get('error', 'An unknown error occurred.')
    return render(request, 'research_support/upload_error.html', {'error': error_message})

@login_required
def upload_pdf(request):
    url_form = UploadPDFUrlForm()
    file_form = UploadPDFForm() 

    if request.method == 'POST':
        # Determine which form is submitted and validate accordingly
        if 'url_submit' in request.POST:
            url_form = UploadPDFUrlForm(request.POST)
            if url_form.is_valid():
                # Process the URL upload
                logger.debug("URL form is being submitted.")
                data = url_form.cleaned_data
                response = upload_pdf_to_ai_pdf_api(data, upload_type='url')
                return handle_upload_response(response, request)
        elif 'file_submit' in request.POST:
            file_form = UploadPDFForm(request.POST, request.FILES)
            if file_form.is_valid() and 'file' in request.FILES:
                logger.info("File form is being submitted with file present in the request.")
                # Extract file from request.FILES and include it in the data to be sent to the API
                data = file_form.cleaned_data
                # data['file'] = request.FILES['file']
                response = upload_pdf_to_ai_pdf_api(data, upload_type='file')
                return handle_upload_response(response, request)

    # For GET request or if neither form is valid, render page with forms
    return render(request, 'research_support/upload_pdf.html', {
        'url_form': url_form, 
        'file_form': file_form
    })

def upload_pdf_to_ai_pdf_api(data, upload_type):
    api_url = 'https://pdf.ai/api/v1/upload/'
    api_key = os.environ.get('PDF_AI_API_KEY')
    if not api_key:
        raise ValueError("No API key set for PDF Ai PDF")
    headers = {'X-API-Key': api_key}
    
    try:
        if upload_type == 'url':
            url_endpoint = api_url + 'url'
            payload = {'url': data['url'], 'isPrivate': data.get('isPrivate', False), 'ocr': data.get('ocr', False)}
            response = requests.post(url_endpoint, json=payload, headers=headers)
        elif upload_type == 'file':
            file_endpoint = api_url + 'file'
            files = {'file': (data['file'].name, data['file'], 'application/pdf')}
            form_data = {'isPrivate': data.get('isPrivate', False), 'ocr': data.get('ocr', False)}
            response = requests.post(file_endpoint, files=files, data=form_data, headers=headers)
        else:
            return {"error": "Invalid upload type specified"}

        # Handle response
        if response.status_code == 200:
            response_data = response.json()
            logger.info("Document uploaded successfully.")
            return response_data
        else:
            logger.error(f"Failed to upload document. Status code: {response.status_code}, Error: {response.text}")
            return {"error": response.text}

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to PDF AI API failed: {e}")
        return {"error": str(e)}



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
    
    pdfs = get_all_pdfs_from_ai_pdf_api(api_key)  # Assuming this fetches data
    
    if 'error' in pdfs:
        # Pass the error message to the template for user-friendly feedback
        return render(request, 'research_support/get_all_pdfs_error.html', {'error': pdfs['error']})
    
    # Pagination setup starts here
    items_per_page = request.GET.get('items_per_page', 10)  # Get items per page from request or use default
    paginator = Paginator(pdfs, int(items_per_page))  # Ensure items_per_page is an integer
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Render the PDFs using the pagination object
    return render(request, 'research_support/get_all_pdfs.html', {'page_obj': page_obj})

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
    # doc_id = request.session.get('docId')
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            docId = form.cleaned_data['docId']
            message = form.cleaned_data['message']
            response = send_chat_request(message, docId)
            if 'error' not in response:  # Check for no error in response
                return render(request, 'research_support/chat_response.html', {'response': response})
            else:
                # Handle error: Show error message in chat form page
                return render(request, 'research_support/chat_with_pdf.html', {'form': form, 'error': response['error']})

    else:
        form = ChatForm()

    return render(request, 'research_support/chat_with_pdf.html', {'form': form})

def send_chat_request(message, doc_id): 
    api_url = 'https://pdf.ai/api/v1/chat'
    api_key = os.environ.get('PDF_AI_API_KEY')
    if  not api_key:
        raise ValueError("No API key set for PDF Ai PDF")       

    payload = {
        'docId': doc_id, # Replace with the actual document ID
        'message': message,
        'save_chat': True, # or False, based on your requirement
        # Add other parameters as needed
        'use_gpt4': True, # or False, based on your requirement
        # 'language': 'en', # or 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru', 'ja', 'ko', 'zh', 'ar', 'tr', 'he', 'id', 'th', 'vi', 'hi', 'bn', 'fa', 'ur', 'ms', 'fil', 'ta', 'te', 'ml', 'kn', 'mr', 'gu', 'pa', 'si', 'my', 'km', 'lo', 'ne
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


def send_summary_request(doc_id):
    api_url = "https://pdf.ai/api/v1/summary/"
    api_key = os.environ.get('PDF_AI_API_KEY')
    if not api_key:
        raise ValueError("No API key set for PDF Ai PDF")

    payload = {
        'docId': doc_id,
        # Remove the 'language' payload if not needed or handle dynamically as required
    }
    headers = {'X-API-Key': api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    # # else:
    # #     logger.error(f"Failed to summarize document. Status code: {response.status_code}, Error: {response.text}")
    # #     return {'error': f'Failed to summarize document. Status code: {response.status_code}'}

    # if response.status_code == 200:
    #     return response.json()
    elif response.status_code == 401:
        return {'error': 'Invalid API key'}
    elif response.status_code == 400:
        return {'error': 'Bad request - missing API key, id, or message'}
    else:
        return {'error': f'Failed to summarize document. Status code: {response.status_code}'}




def summarize_pdf(request):
    # form = SummaryForm(request.POST or None)
    # summary_result = None
    # error_message = None

    if request.method == 'POST':
        form = SummaryForm(request.POST or None)
        if form.is_valid():
            docId = form.cleaned_data['docId']
            response = send_summary_request(docId)
        
        if 'error' not in response:
                return render(request, 'research_support/summary_response.html', {'response': response})

            # summary_result = response.get('content', 'No summary available.')
            # # Instead of dynamically disabling/enabling form fields, consider displaying the summary separately
        else:
            return render(request, 'research_support/summarize_pdf.html', {'form': form, 'error': response['error']})

    else:
        form = SummaryForm()

    return render(request, 'research_support/summarize_pdf.html', {'form': form})

@login_required
def delete_pdf(request, doc_id):
    if request.method == 'POST':
        # Attempt to delete the document from the AI Drive first
        response = delete_pdf_from_ai_pdf_api(doc_id)
        if 'error' in response:
            # If there's an error, inform the user
            messages.error(request, response['error'])
        else:
            # If the API call was successful, delete the document from the Django database
            # pdf = get_object_or_404(PDF, id=doc_id)  # Make sure to use the correct model and field name
            # pdf.delete()
            # Inform the user of success
            messages.success(request, 'PDF deleted successfully.')
            
        # Redirect to the page showing all PDFs
        return redirect('research_support:get_all_pdfs')
    else:
        # If not a POST request, do not allow deletion
        return redirect('research_support:get_all_pdfs')



def delete_pdf_from_ai_pdf_api(doc_id):
    api_url = "https://pdf.ai/api/v1/delete"
    api_key = os.environ.get('PDF_AI_API_KEY')
    if not api_key:
        raise ValueError("No API key set for PDF Ai PDF")

    payload = {'docId': doc_id}

    headers = {
        "X-API-KEY": api_key
    }
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return {"message": response.json().get("message", "Successfully deleted!")}
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
