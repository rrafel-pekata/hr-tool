import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone

from apps.casestudies.models import CandidateCaseStudy
from apps.notifications.services import notify_company
from apps.tenants.models import CompanyMembership

logger = logging.getLogger(__name__)


def portal_case_study(request, token):
    """Portal público: ver y entregar case study."""
    ccs = get_object_or_404(
        CandidateCaseStudy.objects.select_related(
            'case_study', 'candidate', 'candidate__position',
            'candidate__position__company',
        ),
        candidate__portal_token=token,
    )

    company = ccs.candidate.position.company
    expired = ccs.deadline and timezone.now() > ccs.deadline and not ccs.submitted_at

    if request.method == 'POST' and not ccs.submitted_at and not expired:
        submission_text = request.POST.get('submission_text', '').strip()
        submission_file = request.FILES.get('submission_file')
        submission_notes = request.POST.get('submission_notes', '').strip()

        # Must have either text or file
        if not submission_text and not submission_file:
            return render(request, 'portal/case_study.html', {
                'ccs': ccs,
                'case_study': ccs.case_study,
                'company': company,
                'expired': expired,
                'error': 'Debes escribir tu respuesta o adjuntar un archivo.',
            })

        if submission_file:
            ccs.submission_file = submission_file
        ccs.submission_text = submission_text
        ccs.submission_notes = submission_notes
        ccs.submitted_at = timezone.now()
        ccs.save()

        # Update candidate status
        candidate = ccs.candidate
        candidate.status = 'case_submitted'
        candidate.save(update_fields=['status'])

        # In-app notification to all company members
        notify_company(
            company=company,
            title='Caso práctico entregado',
            message=f'{candidate.full_name} ha entregado "{ccs.case_study.title}".',
            link=f'/candidates/{candidate.pk}/',
            notification_type='case_study',
        )

        # Notify recruiters by email
        _notify_submission(request, ccs)

        return render(request, 'portal/confirmation.html', {
            'ccs': ccs,
            'company': company,
        })

    return render(request, 'portal/case_study.html', {
        'ccs': ccs,
        'case_study': ccs.case_study,
        'company': company,
        'expired': expired,
    })


def _notify_submission(request, ccs):
    """Notificar a los reclutadores que el candidato ha entregado."""
    candidate = ccs.candidate
    company = candidate.position.company

    # Get all users in this company
    memberships = CompanyMembership.objects.filter(company=company).select_related('user')
    recipient_emails = [m.user.email for m in memberships if m.user.email]

    if not recipient_emails:
        return

    candidate_url = request.build_absolute_uri(
        f'/candidates/{candidate.pk}/'
    )

    html_content = render_to_string('emails/casestudy_submitted.html', {
        'candidate_name': candidate.full_name,
        'casestudy_title': ccs.case_study.title,
        'position_title': candidate.position.title,
        'submitted_at': ccs.submitted_at.strftime('%d/%m/%Y a las %H:%M'),
        'candidate_url': candidate_url,
    })

    try:
        send_mail(
            subject=f'Caso práctico entregado — {candidate.full_name} — {candidate.position.title}',
            message=f'{candidate.full_name} ha entregado el caso práctico "{ccs.case_study.title}".',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_emails,
            html_message=html_content,
            fail_silently=True,
        )
    except Exception:
        logger.exception("Error enviando notificación de entrega de case study")
