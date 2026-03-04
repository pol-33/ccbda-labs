from django.http import HttpResponse
from django.shortcuts import render
from .models import Leads
import logging
from django.conf import settings
from collections import Counter

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

def search(request):
    domain = request.GET.get('domain')
    preview = request.GET.get('preview')
    leads = Leads()
    items = leads.get_leads(domain, preview)
    if domain or preview:
        return render(request, 'form/search.html', {'items': items})
    else:
        domain_count = Counter()
        domain_count.update([
            item['email'].split('@')[1]
            for item in items
            if item.get('email') and '@' in item.get('email', '') and item['email'].split('@')[1]
            # Ensure domain part is not empty
        ])
        return render(request, 'form/search.html', {'domains': sorted(domain_count.items())})