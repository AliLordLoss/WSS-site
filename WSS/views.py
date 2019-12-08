from random import Random
from itertools import groupby
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.shortcuts import redirect
import logging

logger = logging.getLogger('payment')
from zeep import Client
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from WSS.forms import ParticipantForm
from WSS.mixins import FooterMixin, WSSWithYearMixin
from WSS.models import WSS, Participant, Grade, Reserve, ShortLink


class HomeView(FooterMixin, DetailView):
    template_name = 'WSS/home.html'
    context_object_name = 'wss'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_seminars'] = self.object.non_keynote_seminars.order_by('?')[:8]
        return context

    def get_object(self, queryset=None):
        if 'year' in self.kwargs:
            return get_object_or_404(WSS, year=int(self.kwargs['year']))
        return WSS.objects.first()


class AboutView(FooterMixin, DetailView):
    template_name = 'WSS/about_us.html'
    model = WSS
    context_object_name = 'wss'

    def get_object(self, queryset=None):
        #TODO: I didn't know how to handle this, so I used a simple trick.
        return get_object_or_404(WSS, year=2019)


class SeminarsListView(FooterMixin, DetailView):
    template_name = 'WSS/seminars_list.html'
    model = WSS
    context_object_name = 'wss'

    def get_object(self, queryset=None):
        return get_object_or_404(WSS, year=int(self.kwargs['year']))


class PosterSessionsListView(FooterMixin, DetailView):
    template_name = 'WSS/postersessions_list.html'
    model = WSS
    context_object_name = 'wss'

    def get_object(self, queryset=None):
        return get_object_or_404(WSS, year=int(self.kwargs['year']))


class WorkshopsListView(FooterMixin, DetailView):
    template_name = 'WSS/workshops_list.html'
    model = WSS
    context_object_name = 'wss'

    def get_object(self, queryset=None):
        return get_object_or_404(WSS, year=int(self.kwargs['year']))


class StaffListView(FooterMixin, DetailView):
    template_name = 'WSS/staff_list.html'
    model = WSS
    context_object_name = 'wss'

    def get_object(self, queryset=None):
        return get_object_or_404(WSS, year=int(self.kwargs['year']))


class GalleryImageView(FooterMixin, WSSWithYearMixin, DetailView):
    template_name = 'WSS/gallery_images.html'


class GalleryVideoView(FooterMixin, WSSWithYearMixin, DetailView):
    template_name = 'WSS/gallery_videos.html'


class ScheduleView(FooterMixin, WSSWithYearMixin, DetailView):
    template_name = 'WSS/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        wss = self.object
        all_events = wss.events.filter(start_time__isnull=False)

        context['pre_wss_events'] = all_events.filter(start_time__date__lt=wss.start_date)
        main_events = all_events.exclude(start_time__date__lt=wss.start_date)

        # Important: I assumed that events with same start_time will have same end_time
        events_by_day = groupby(groupby(main_events, lambda event: event.start_time),
                                lambda group: group[0].date())

        # Surprising bug made me do this! I have know idea why I should reiterate events_by_day!
        context['events_by_day'] = []
        for date, events_by_time in events_by_day:
            print(date)
            _events_by_time = []
            for time, events in events_by_time:
                _events_by_time.append((time, list(events)))  # OMG! casting to list is important!!
            context['events_by_day'].append((date, _events_by_time))
        return context


class ReserveView(FooterMixin, WSSWithYearMixin, DetailView):
    template_name = 'WSS/reserve.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['form'] = ParticipantForm()
        return render(self.request, self.template_name, {'form': ParticipantForm()})


class RegisterView(FooterMixin, WSSWithYearMixin, DetailView):
    template_name = 'WSS/register.html'


MERCHANT = '5ff4f360-c10a-11e9-af68-000c295eb8fc'
client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
student_price = 100
other_price = 100


@csrf_exempt
def send_request(request, year):
    form = ParticipantForm(request.POST)
    if not form.is_valid():
        return HttpResponse("form is not valid")

    CallbackURL = 'http://http://wss.ce.sharif.edu/' + str(
        year) + '/verify/'  # Important: need to edit for realy server.

    name_family = form.data['name_family']
    email = form.data['email']
    grade = form.data['grade']
    phone_number = form.data['phone_number']
    job = form.data['job']
    university = form.data['university']
    introduction_method = form.data['introduction_method']
    gender = form.data['gender']
    home_city = form.data['city']
    country = form.data['country']
    field_of_interest = form.data['interests']
    is_student = bool(form.data['is_student'])
    logger.info("participant with email:" + email + " created.")

    try:
        exh = Participant.objects.all().get(email=email)
    except Participant.DoesNotExist:
        exh = None
    if exh is not None and exh.payment_status == 'OK':
        return HttpResponse('ثبت نام انجام شده است. ایمیل تکراری است.')
    try:
        gr = Grade.objects.all().get(level=grade)
    except Grade.DoesNotExist:
        return HttpResponse('مدرک تحصیلی درست وارد نشده است.')

    cap = gr.capacity
    if cap <= 0:
        return reserve(form)
        pass
    price = student_price
    if not is_student:
        price = other_price

    payment_id = Random().randint(0, 1000000000)
    exh = Participant(name_family=name_family, email=email, grade=grade, phone_number=phone_number, job=job,
                      university=university, introduction_method=introduction_method, gender=gender,
                      home_city=home_city, payment_id=payment_id,
                      country=country, field_of_interest=field_of_interest, is_student=is_student)
    exh.save()
    result = client.service.PaymentRequest(MERCHANT, price, description, email, phone_number,
                                           CallbackURL + email)
    if result.Status == 100:
        logger.info("user with email:" + email + " connected to payment")
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))  # todo move to error page


def verify(request, year, email):
    logger.info("participant with email:" + email + " starting to verify.")

    try:
        exh = Participant.objects.all().get(email=email)
    except Participant.DoesNotExist:
        return HttpResponse('پرداخت با خطا مواجه شد. با پشتیبانی تماس بگیرید.')  # todo  move to error page

    price = other_price
    if exh.is_student:
        price = student_price

    if request.GET.get('Status') == 'OK':
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], price)
        if result.Status == 100:

            exh.payment_status = 'OK'
            exh.save()

            gr = Grade.objects.all().get(level=exh.grade)
            gr.capacity -= 1
            gr.save()

            logger.info("participant with email:" + email + " verified successfully.")
            return HttpResponse(
                'Transaction success.\nRefID: ' + str(result.RefID))  # todo redirect secsucess full payment
        elif result.Status == 101:
            logger.info(
                "participant with email:" + email + " verified again. perhaps he attacking us.")  # todo redirect to tekrari

            return HttpResponse('Transaction submitted : ' + str(result.Status))
        else:
            logger.info("participant with email:" + email + " don't verified")
            return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status)) # todo redirect to error page
    else:
        logger.info("participant with email:" + email + " don't verified")
        return HttpResponse('Transaction failed or canceled by user') # todo redirect to error page


def reserve(form):
    email = form.data['email']
    name_family = form.data['name_family']
    grade = form.data['grade']
    Reserve(name=name_family, email=email, grade=grade).save()
    return HttpResponse('درصورت وجود ظرفیت مازاد به شما اطلاع رسانی خواهیم کرد.')  # todo error page


def go(request, year, url):
    link = None
    try:
        link = ShortLink.objects.all().get(short_link=url)
    except:
        return redirect(NotFound())  # todo 404 page
    return redirect(to=link.url)


class NotFound(FooterMixin, WSSWithYearMixin, DetailView):
    template_name = '../templates/404.html'