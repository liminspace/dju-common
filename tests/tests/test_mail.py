# coding=utf-8
import pytz
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core import mail
from django.utils import timezone
from dju_common.mail import send_mail, RenderMailSender, attach_html_wrapper


class TestSendMail(TestCase):
    def test_send_mail_simple(self):
        subject = 'Test subject'
        send_mail(subject, 'body 1 ...', 'test@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + subject)

    def test_send_mail_with_attach(self):
        subject = 'Test subject 2'
        attach_html = attach_html_wrapper(
            '<p class="test">Attach html doc</p>',
            title='Test html attach',
            head='<style>.test {font-size: 20px;}</style>'
        )
        send_mail(subject, 'body 2 ...', 'test1@mail.com',
                  attach_alternative=(('<p>body 2 ...</p>', 'text/html'),),
                  attaches=(('file.txt', attach_html, 'text/html'),))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + subject)


class TestRenderMailSender(TestCase):
    class R(object):
        pass

    def test_render_mail(self):
        t = RenderMailSender('mail/test1.html', context={
            'm': 'test',
        })
        t.send('test3@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + 'Test subject 1 test')

    def test_configure(self):
        for kw in ({'tpl_fn': 'mail/test1.html'}, {'lang': 'en'}, {'tz': 'Europe/London'}):
            t = RenderMailSender('mail/test1.html')
            t.send('test3@mail.com')
            self.assertIsNotNone(t._tpl)
            self.assertIsNotNone(t._render_cache)
            t.configure(**kw)
            self.assertIsNone(t._tpl)
            self.assertIsNone(t._render_cache)
        for kw in ({'request': 'Request'}, {'context': {'a': 1}}):
            t = RenderMailSender('mail/test1.html')
            t.send('test3@mail.com')
            self.assertIsNotNone(t._context_cache)
            self.assertIsNotNone(t._render_cache)
            t.configure(**kw)
            self.assertIsNone(t._context_cache)
            self.assertIsNone(t._render_cache)
        t = RenderMailSender('mail/test1.html')
        with self.assertRaises(AttributeError):
            t.configure(abracadabra=1)

    def test_render_mail_with_request(self):
        t = RenderMailSender('mail/test1.html', request=self.R(), context={
            'm': 'test2',
        })
        t.send('test4@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + 'Test subject 1 test2')

    def test_render_mail_with_tz(self):
        now = timezone.now()
        t = RenderMailSender('mail/test2.html', context={'now': now})
        t.send('test5@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + 'Test subject 2')
        self.assertTrue(now.strftime('%Y.%m.%d %H:%M:%S') in mail.outbox[0].body)
        mail.outbox = []
        t = RenderMailSender('mail/test2.html', context={'now': now}, tz='Europe/Warsaw')
        t.send('test5@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + 'Test subject 2')
        self.assertTrue(
            now.astimezone(pytz.timezone('Europe/Warsaw')).strftime('%Y.%m.%d %H:%M:%S') in mail.outbox[0].body
        )

    def test_render_mail_with_lang(self):
        t = RenderMailSender('mail/test3.html')
        t.send('test6@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + 'Test subject 3')
        self.assertTrue(u'Phone number' in mail.outbox[0].body)
        mail.outbox = []
        t = RenderMailSender('mail/test3.html', lang='uk')
        t.send('test6@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + 'Test subject 3')
        self.assertTrue(u'Номер телефону' in mail.outbox[0].body)

    def test_render_mail_render_error(self):
        for i in range(1, 4):
            t = RenderMailSender('mail/test_invalid_{}.html'.format(i))
            with self.assertRaises(t.TemplateEmailTagNotFound):
                t.send('testerror{}@mail.com'.format(i))

    def test_render_mail_context_proccessors_without_request(self):
        t = RenderMailSender('mail/test4.html')
        t.send('test7@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + 'Test subject 4')
        self.assertTrue('STATIC_CP_VALUE_OK' in mail.outbox[0].body)

    def test_render_mail_context_proccessors_with_request(self):
        t = RenderMailSender('mail/test4.html', request=self.R())
        t.send('test8@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_SUBJECT_PREFIX + 'Test subject 4')
        self.assertTrue('STATIC_CP_VALUE_OK' in mail.outbox[0].body)

    def test_render_mail_and_url_tag(self):
        t = RenderMailSender('mail/test5.html')
        t.send('test9@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(reverse('test_page'), mail.outbox[0].body)

    def test_render_mail_using_cache(self):
        t = RenderMailSender('mail/test1.html')
        self.assertIsNone(t._render_cache)
        self.assertIsNone(t._context_cache)
        t.send('test10@mail.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIsNotNone(t._render_cache)
        self.assertIsNotNone(t._context_cache)
        t.send('test10@mail.com')
        self.assertEqual(len(mail.outbox), 2)
