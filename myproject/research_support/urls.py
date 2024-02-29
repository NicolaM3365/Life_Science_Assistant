from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('research-support/', views.index, name='index'),
    path('about/', views.about, name='about'),
    # path('contact/', views.contact, name='contact'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    # URL pattern for displaying the chat form
    path('chat-with-pdfs/', views.chat_with_pdfs, name='chat_with_pdfs'),

    # URL pattern for processing the chat input and displaying the response
    # path('process-chat/', views.process_chat, name='process_chat'),

    # In urls.py

    path('delete-pdf/<str:file_name>/', views.delete_pdf, name='delete_pdf'),

    # path('upload-pdf-and-get-doc-id/', views.upload_pdf_and_get_doc_id, name='upload_pdf_and_get_doc_id'),

    path('upload-pdf/success/', views.success_page, name='upload_pdf_success'),
    
    path('summarize-pdf/', views.summarize_pdf, name='summarize_pdf'),
    path('summarize-pdf/success/', views.success_page, name='summarize_pdf_success'),
    

    path('search/', views.search, name='search'),
    path('upload-pdf-to-ai-pdf-api/', views.upload_pdf_to_ai_pdf_api, name='upload_pdf_to_ai_pdf_api'),
    path('pdfs/', views.pdfs, name='pdfs'),
    path('success/', views.success_page, name='success_url'),
    path('upload-error/', views.upload_error, name='upload_error')



    # path('upload/', views.upload, name='upload'),
    # path('document/<int:document_id>/', views.document, name='document'),
    # path('document/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    # path('document/<int:document_id>/summary/', views.summary, name='summary'),
    # path('document/<int:document_id>/tag/', views.tag, name='tag'),
    # path('document/<int:document_id>/related/', views.related, name='related'),
    # path('document/<int:document_id>/vector/', views.vector, name='vector'),
    # path('document/<int:document_id>/qa/', views.qa, name='qa'),
    # path('document/<int:document_id>/feedback/', views.feedback, name='feedback'),
    # path('document/<int:document_id>/query/', views.query, name='query'),
    # path('document/<int:document_id>/pdf/', views.pdf_detail, name='pdf_detail'),
    # path('document/<int:document_id>/pdf/download/', views.download_pdf, name='download_pdf'),
    # path('document/<int:document_id>/pdf/delete/', views.delete_pdf, name='delete_pdf'),
    # path('document/<int:document_id>/image/', views.image, name='image'),
    # path('document/<int:document_id>/image/delete/', views.delete_image, name='delete_image'),
    # path('document/<int:document_id>/image/download/', views.download_image, name='download_image'),
]
