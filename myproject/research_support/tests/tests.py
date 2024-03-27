
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from unittest.mock import patch
from research_support.models import PDF, ChatHistory, Summary
from research_support.forms import SearchForm, UploadPDFUrlForm, UploadPDFForm, DeletePDFForm, ChatForm, SummaryForm



class SearchFormTest(TestCase):

    def test_search_form_valid(self):
        form = SearchForm(data={'search': 'test query'})
        self.assertTrue(form.is_valid())

    def test_search_form_empty(self):
        form = SearchForm(data={'search': ''})
        self.assertFalse(form.is_valid())  # Assuming you want to require a search query

class UploadPDFUrlFormTest(TestCase):

    def test_upload_pdf_url_form_valid(self):
        form = UploadPDFUrlForm(data={'url': 'http://example.com/test.pdf', 'isPrivate': True, 'ocr': True})
        self.assertTrue(form.is_valid())

    def test_upload_pdf_url_form_invalid_url(self):
        form = UploadPDFUrlForm(data={'url': 'not_a_valid_url', 'isPrivate': False, 'ocr': False})
        self.assertFalse(form.is_valid())

class UploadPDFFormTest(TestCase):

    def test_upload_pdf_form_valid(self):
        file_data = SimpleUploadedFile("test.pdf", b"pdf_file_content", content_type="application/pdf")
        form = UploadPDFForm(data={'isPrivate': True, 'ocr': False}, files={'file': file_data})
        self.assertTrue(form.is_valid())

    def test_upload_pdf_form_no_file(self):
        form = UploadPDFForm(data={'isPrivate': True, 'ocr': False})
        self.assertFalse(form.is_valid())

class DeletePDFFormTest(TestCase):

    def test_delete_pdf_form_valid(self):
        form = DeletePDFForm(data={'docId': '12345'})
        self.assertTrue(form.is_valid())

    def test_delete_pdf_form_empty(self):
        form = DeletePDFForm(data={'docId': ''})
        self.assertFalse(form.is_valid())

class ChatFormTest(TestCase):

    def test_chat_form_valid(self):
        form = ChatForm(data={'docId': '12345', 'message': 'Hello, this is a test message.', 'save_chat': True, 'use_gpt4': True})
        self.assertTrue(form.is_valid())

    def test_chat_form_empty_message(self):
        form = ChatForm(data={'docId': '12345', 'message': '', 'save_chat': False, 'use_gpt4': False})
        self.assertFalse(form.is_valid())


class SummaryFormTest(TestCase):

    def test_summary_form_valid(self):
        form_data = {
            'docId': '12345',
            'summary': ''  # Even though the summary is not required, it's still part of the form.
        }
        form = SummaryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_summary_form_missing_docId(self):
        form = SummaryForm(data={'docId': '', 'summary': 'Automatically generated summary.'})
        self.assertFalse(form.is_valid())




# Create a test case class for your app
class ResearchSupportViewTests(TestCase):
    def setUp(self):
        # Create a user for tests that require authentication
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()

    def test_success_page(self):
        response = self.client.get(reverse('success_url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'research_support/success.html')


    def test_index_view(self):
        response = self.client.get(reverse('research_support:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'research_support/index.html')


    def test_about_view(self):
        response = self.client.get(reverse('research_support:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'research_support/about.html')

    def test_search_view_get(self):
        response = self.client.get(reverse('research_support:search'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], SearchForm)

    # def test_search_view_post(self):
    #     response = self.client.post(reverse('research_support:search'), {'query': 'test'})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue('results' in response.context)


    def test_pdf_options_authenticated(self):
        self.client.login(username='testuser', password='password123')
        pdf = PDF.objects.create( # Create a test PDF object
            # Set attributes as necessary
        )
        response = self.client.get(reverse('research_support:pdf_options', kwargs={'doc_id': pdf.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'research_support/pdf_options.html')

    def test_pdf_options_unauthenticated(self):
        pdf = PDF.objects.create( # Create a test PDF object
            # Set attributes as necessary
        )
        response = self.client.get(reverse('research_support:pdf_options', kwargs={'doc_id': pdf.id}))
        self.assertNotEqual(response.status_code, 200)  # Assuming redirection or access denied


    def test_upload_error(self):
        response = self.client.get(reverse('research_support:upload_error') + '?error=test+error')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'research_support/upload_error.html')
        self.assertIn('test error', response.context['error'])



class UploadPDFTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for authentication
        cls.user = User.objects.create_user(username='testuser', password='12345')
    

def test_upload_pdf_redirect_if_not_logged_in(self):
    # Reverse the 'login' URL name to get the actual path
    login_url = reverse('login')
    # Reverse the 'research_support:upload_pdf' URL name to get the actual path for the next parameter
    upload_pdf_url = reverse('research_support:upload_pdf')
    # Construct the expected redirect URL
    expected_redirect_url = f"{login_url}?next={upload_pdf_url}"
    
    # Perform the test action
    response = self.client.get(upload_pdf_url)
    
    # Test whether the response redirects as expected
    self.assertRedirects(response, expected_redirect_url, fetch_redirect_response=False)


    def test_load_upload_page_for_authenticated_user(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('research_support:upload_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'research_support:upload_pdf')
    
    @patch('research_support/views.upload_pdf_to_ai_pdf_api')
    def test_upload_pdf_url_success(self, mock_upload):
        mock_upload.return_value = {'status': 'success'}
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('research_support:upload_pdf'), {'url': 'http://example.com/test.pdf', 'url_submit': True})
        # Assuming you redirect to a success page on successful upload
        self.assertRedirects(response, reverse('research_support:upload_success'))

    @patch('research_support/views.upload_pdf_to_ai_pdf_api')
    def test_upload_pdf_file_success(self, mock_upload):
        mock_upload.return_value = {'status': 'success'}
        self.client.login(username='testuser', password='12345')
        with open('research_support/tests/test_files/dummy.pdf', 'rb') as file:
            response = self.client.post(reverse('research_support:upload_pdf'), {'file': file, 'file_submit': True})
            # Assuming you redirect to a success page on successful upload
            self.assertRedirects(response, reverse('research_support:upload_success'))


    @patch('research_support/views.upload_pdf_to_ai_pdf_api')
    def test_upload_pdf_api_error(self, mock_upload):
        mock_upload.return_value = {"error": "API error occurred"}
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('research_support:upload_pdf'), {'url': 'http://example.com/faulty.pdf', 'url_submit': True})
        self.assertEqual(response.status_code, 200)  # Assuming the page reloads with an error message
        self.assertContains(response, "API error occurred")

    def test_upload_pdf_url_form_invalid(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('research_support:upload_pdf'), {'url': 'not_a_valid_url', 'url_submit': True})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('url_form' in response.context)
        self.assertFalse(response.context['url_form'].is_valid())
        self.assertContains(response, "Enter a valid URL.")


    @patch('research_support.views.upload_pdf_to_ai_pdf_api')
    def test_upload_pdf_success_redirect(self, mock_upload):
        mock_upload.return_value = {'status': 'success'}
        self.client.login(username='testuser', password='12345')
        with open('research_support/tests/test_files/dummy.pdf', 'rb') as file:
            response = self.client.post(reverse('research_support:upload_pdf'), {'file': file, 'file_submit': True})
        self.assertRedirects(response, reverse('research_support:upload_success'))  # Ensure this is the correct redirect




class ChatWithPdfTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user = User.objects.create_user(username='testuser', password='12345')




    def test_chat_with_pdf_view_no_login_redirect(self):
        # Generate the URL for the view you're testing access to
        chat_with_pdf_url = reverse('research_support:chat_with_pdf')
        # Generate the expected login URL, including the 'next' parameter with the URL you're testing
        login_url = reverse('login')  # Use the name you've configured for your login view
        expected_redirect_url = f'{login_url}?next={chat_with_pdf_url}'
        
        # Perform the test action
        response = self.client.get(chat_with_pdf_url)
        
        # Test whether the response redirects as expected
        self.assertRedirects(response, expected_redirect_url, fetch_redirect_response=False)


class ChatWithPdfTests(TestCase):
    def setUp(self):
        # Set up test user
        self.user = User.objects.create_user(username='testuser', password='12345')
    
    @patch('research_support.views.send_chat_request')
    def test_chat_with_pdf_post_valid(self, mock_send_chat_request):
        # Mock the send_chat_request method to return a simulated API response
        mock_send_chat_request.return_value = {
            "content": "Mocked API Response",
            "references": [{"pageNumber": 1, "fromLine": 2, "toLine": 3}]
        }

        self.client.login(username='testuser', password='12345')
        url = reverse('research_support:chat_with_pdf')
        data = {
            'docId': 'test_doc_id',
            'message': 'Hello, world!',
            'save_chat': True,
            'use_gpt4': False,
        }
        response = self.client.post(url, data)

        # Ensure the form submission is successful and the expected template is rendered
        self.assertEqual(response.status_code, 200)
        # Check that the template used is the expected one for a successful chat response
        self.assertTemplateUsed(response, 'research_support/chat_response.html')
        # Check for presence of 'Mocked API Response' in the rendered template
        self.assertContains(response, 'Mocked API Response')



class ChatWithPdfTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_chat_with_pdf_post_invalid_form(self):
        # Log in the test user
        self.client.login(username='testuser', password='12345')

        # Define the URL for the chat_with_pdf view
        url = reverse('research_support:chat_with_pdf')

        # Prepare invalid form data (e.g., missing required 'message' field)
        data = {
            'docId': 'test_doc_id',  # Assuming 'docId' is valid but 'message' is missing or invalid
            # 'message': 'This would be intentionally left out or made invalid for the test',
            'save_chat': True,
            'use_gpt4': False,
        }

        # Submit the form with invalid data
        response = self.client.post(url, data)

        # Verify that the response status code is 200, indicating the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)

        # Optionally, check for the presence of form errors in the response context
        self.assertTrue('form' in response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)

        # If you want to be more specific, you can check for errors on the expected fields
        # Example:
        # self.assertIn('message', response.context['form'].errors)


@patch('research_support.views.requests.post')
def test_chat_with_pdf_api_error(self, mock_post):
    # Simulate an API error response
    mock_post.return_value.status_code = 500
    mock_post.return_value.json.return_value = {'error': 'Internal server error'}

    self.client.login(username='testuser', password='12345')
    url = reverse('research_support:chat_with_pdf')
    data = {
        'docId': 'test_doc_id',
        'message': 'Hello, world!',
        'save_chat': True,
        'use_gpt4': False,
    }
    response = self.client.post(url, data)

    # Verify that the view handles the API error as expected
    self.assertTemplateUsed(response, 'research_support/chat_with_pdf.html')
    self.assertIn('error', response.context)
    self.assertEqual(response.context['error'], 'Internal server error')

def test_chat_with_pdf_invalid_form_submission(self):
    self.client.login(username='testuser', password='12345')
    url = reverse('research_support:chat_with_pdf')
    invalid_data = {
        # Assuming 'message' is a required field
        'docId': 'test_doc_id',
        'save_chat': True,
        'use_gpt4': False,
    }
    response = self.client.post(url, invalid_data)

    # Check that the response indicates the form submission was invalid
    self.assertEqual(response.status_code, 200)
    self.assertTrue('form' in response.context)
    self.assertFalse(response.context['form'].is_valid())
    self.assertIn('message', response.context['form'].errors)



class ResearchSupportViewTests(TestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    @patch('research_support.views.send_summary_request')
    def test_summarize_pdf_api_error(self, mock_send_summary):
        # Configure the mock to return an error response
        mock_send_summary.return_value = {'error': 'API error occurred'}
        
        # Make a POST request to the summarize_pdf view with test data
        response = self.client.post(reverse('research_support:summarize_pdf'), {'docId': 'test_doc_id'})

        # Check that the error message is in the response
        # Since the error is added to the form, we should check if the form's error is rendered in the template
        self.assertFormError(response, 'form', None, 'API error occurred')

        # Additionally, verify that the correct template was used to render the response
        self.assertTemplateUsed(response, 'research_support/summarize_pdf.html')


    def test_summarize_pdf_invalid_form(self):
        url = reverse('research_support:summarize_pdf')
        response = self.client.post(url, {'docId': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'research_support/summarize_pdf.html')
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('docId', response.context['form'].errors)

    @patch('research_support.views.delete_pdf_from_ai_pdf_api')
    def test_delete_pdf(self, mock_delete):
        # Mock the API call to simulate a successful deletion
        mock_delete.return_value = {'message': 'Successfully deleted!'}
        doc_id = 'dummy_doc_id'  # Assuming you have a way to specify or create a doc ID for testing
        url = reverse('research_support:delete_pdf', kwargs={'doc_id': doc_id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('research_support:get_all_pdfs'), status_code=302, target_status_code=200)

    
# class PDFModelTests(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         # Setup non-modified objects used by all test methods
#         cls.pdf = PDF.objects.create(file_name="test.pdf", text_content="Sample text")

#     def test_pdf_content(self):
#         self.assertEqual(self.pdf.file_name, "test.pdf")
#         self.assertEqual(self.pdf.text_content, "Sample text")

#     def test_str_method(self):
#         self.assertEqual(str(self.pdf), "test.pdf")

#     @classmethod
#     def setUpTestData(cls):
#         cls.user = User.objects.create_user(username='testuser', password='12345')
#         cls.chathistory = ChatHistory.objects.create(
#             user=cls.user,
#             docId='Document Id',
#             message ='This is a test chat prompt',
#             response='This is a test chat response',
#             created_at='2022-01-01 00:00:00'

#     )

# class UploadPDFFormTest(TestCase):

#     def test_form_validity(self):
#         form_data = {'file': SimpleUploadedFile("test.pdf", b"file_content"), 'isPrivate': False, 'ocr': False}
#         form = UploadPDFForm(data=form_data)
#         self.assertTrue(form.is_valid())



# class UploadPDFViewTests(TestCase):

#     def setUp(self):
#         # Create a user for authentication
#         self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
#         self.client = Client()
#         self.upload_url = reverse('upload_pdf')

#     def test_upload_pdf_view_get_request(self):
#         self.client.login(username='testuser', password='testpassword')
#         response = self.client.get(self.upload_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'research_support/upload_pdf.html')
#         self.assertIsInstance(response.context['url_form'], UploadPDFUrlForm)
#         self.assertIsInstance(response.context['file_form'], UploadPDFForm)

#     def test_upload_pdf_url_form_post_request(self):
#         self.client.login(username='testuser', password='testpassword')
#         data = {'url': 'http://example.com/test.pdf', 'isPrivate': True, 'ocr': True, 'url_submit': True}
#         response = self.client.post(self.upload_url, data)
#         # Assuming handle_upload_response redirects or renders a specific template upon success
#         self.assertEqual(response.status_code, 302)  # or check for specific template

#     def test_upload_pdf_file_form_post_request(self):
#         self.client.login(username='testuser', password='testpassword')
#         file_data = SimpleUploadedFile("test.pdf", b"pdf file content", content_type="application/pdf")
#         data = {'file': file_data, 'isPrivate': False, 'ocr': False, 'file_submit': True}
#         response = self.client.post(self.upload_url, data, follow=True)
#         # Assuming handle_upload_response redirects or renders a specific template upon success
#         self.assertEqual(response.status_code, 302)  # or check for specific template

#     def test_upload_pdf_view_redirect_if_not_logged_in(self):
#         response = self.client.get(self.upload_url)
#         self.assertRedirects(response, f'/accounts/login/?next={self.upload_url}')
