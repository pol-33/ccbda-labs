from django.http import HttpResponse
from django.shortcuts import render
from .models import Leads
import logging
from django.conf import settings

logger = logging.getLogger('django')

def home(request):
    logger.info('Home page accessed')

    context = {
        'cloudfront_id': settings.CLOUDFRONT_DISTRIBUTION_ID,
    }

    return render(request, 'form/index.html', context)


def signup(request):
    leads = Leads()
    status = leads.insert_lead(request.POST['name'], request.POST['email'], request.POST['previewAccess'])
    if status == 200:
        leads.send_notification(request.POST['email'])
    return HttpResponse('', status=status)
