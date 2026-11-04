from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from restaurant.models import Menu, Booking
from restaurant.serializers import MenuSerializer

class MenuModelTests(TestCase):
    def test_menu_representation(self):
        item = Menu.objects.create(title='Ice Cream', price=Decimal('80.00'), inventory=100)
        self.assertEqual(str(item), 'Ice Cream : 80.00')
        self.assertEqual(MenuSerializer(item).data['price'], '80.00')

class RestaurantAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(username='guest', password='Long-Test-Pass-923!')
        self.other = get_user_model().objects.create_user(username='other', password='Long-Test-Pass-923!')
        self.staff = get_user_model().objects.create_user(username='chef', password='Long-Test-Pass-923!', is_staff=True)
        self.item = Menu.objects.create(title='Greek Salad', price='12.50', inventory=10)
        self.booking_data = {'name': 'Guest', 'no_of_guests': 2, 'booking_date': '2030-12-20T19:00:00Z'}
    def authenticate(self, user=None):
        token, _ = Token.objects.get_or_create(user=user or self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return token.key
    def test_home_renders_static_html(self):
        response = self.client.get('/')
        self.assertContains(response, 'Little Lemon')
        self.assertContains(response, '/static/restaurant/style.css')
        self.assertTemplateUsed(response, 'restaurant/index.html')
    def test_menu_requires_authentication(self):
        self.assertEqual(self.client.get(reverse('menu-list')).status_code, 401)
        self.assertEqual(self.client.get(reverse('menu-detail', args=[self.item.pk])).status_code, 401)
    def test_invalid_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid')
        self.assertEqual(self.client.get(reverse('menu-list')).status_code, 401)
    def test_registration_hashes_password(self):
        response = self.client.post(reverse('register'), {'username': 'newguest', 'password': 'Unique-Food-1937!'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        self.assertTrue(get_user_model().objects.get(username='newguest').check_password('Unique-Food-1937!'))
        self.assertFalse(get_user_model().objects.get(username='newguest').is_staff)
    def test_registration_rejects_duplicate_and_weak_password(self):
        for data in [{'username': 'guest', 'password': 'Unique-Food-1937!'}, {'username': 'newguest', 'password': '123'}]:
            self.assertEqual(self.client.post(reverse('register'), data).status_code, 400)
    def test_login_logout_revokes_token(self):
        response = self.client.post(reverse('token-login'), {'username': 'guest', 'password': 'Long-Test-Pass-923!'})
        self.assertEqual(response.status_code, 200)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(self.client.get(reverse('menu-list')).status_code, 200)
        self.assertEqual(self.client.post(reverse('token-logout')).status_code, 204)
        self.assertEqual(self.client.get(reverse('menu-list')).status_code, 401)
    def test_bad_login_rejected(self):
        self.assertEqual(self.client.post(reverse('token-login'), {'username':'guest','password':'wrong'}).status_code, 400)
    def test_guest_can_read_but_not_write_menu(self):
        self.authenticate()
        response = self.client.get(reverse('menu-list'))
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Greek Salad')
        self.assertEqual(self.client.post(reverse('menu-list'), {'title':'Cake','price':'5.00','inventory':3}).status_code, 403)
        self.assertEqual(self.client.delete(reverse('menu-detail', args=[self.item.pk])).status_code, 403)
    def test_staff_menu_crud(self):
        self.authenticate(self.staff)
        response = self.client.post(reverse('menu-list'), {'title':'Cake','price':'5.00','inventory':3})
        self.assertEqual(response.status_code, 201)
        url = reverse('menu-detail', args=[response.data['id']])
        self.assertEqual(self.client.get(url).data['title'], 'Cake')
        self.assertEqual(self.client.patch(url, {'price':'6.00'}).data['price'], '6.00')
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)
    def test_invalid_menu_values(self):
        self.authenticate(self.staff)
        for price, inventory in [('-1.00',1),('2.00',-1)]:
            self.assertEqual(self.client.post(reverse('menu-list'), {'title':'Cake','price':price,'inventory':inventory}).status_code, 400)
    def test_booking_requires_authentication(self):
        self.assertEqual(self.client.get(reverse('booking-list')).status_code, 401)
        self.assertEqual(self.client.post(reverse('booking-list'), self.booking_data).status_code, 401)
    def test_guest_booking_crud_and_owner_cannot_be_spoofed(self):
        self.authenticate()
        response = self.client.post(reverse('booking-list'), {**self.booking_data, 'owner':self.other.pk})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['owner'], self.user.pk)
        url = reverse('booking-detail', args=[response.data['id']])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.patch(url, {'no_of_guests':4}).data['no_of_guests'], 4)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertFalse(Booking.objects.exists())
    def test_other_users_cannot_read_or_change_booking(self):
        booking = Booking.objects.create(owner=self.other, name='Other', no_of_guests=2, booking_date=timezone.now())
        self.authenticate()
        self.assertEqual(self.client.get(reverse('booking-list')).data['count'], 0)
        url = reverse('booking-detail', args=[booking.pk])
        for response in [self.client.get(url), self.client.patch(url, {'name':'Changed'}), self.client.delete(url)]:
            self.assertEqual(response.status_code, 404)
        self.assertTrue(Booking.objects.filter(pk=booking.pk).exists())
    def test_staff_can_manage_all_bookings(self):
        booking = Booking.objects.create(owner=self.other, name='Other', no_of_guests=2, booking_date=timezone.now())
        self.authenticate(self.staff)
        self.assertEqual(self.client.get(reverse('booking-list')).data['count'], 1)
        self.assertEqual(self.client.patch(reverse('booking-detail', args=[booking.pk]), {'no_of_guests':3}).status_code, 200)
    def test_invalid_booking_values(self):
        self.authenticate()
        for fields in [{'no_of_guests':0},{'no_of_guests':21},{'booking_date':'invalid'}]:
            self.assertEqual(self.client.post(reverse('booking-list'), {**self.booking_data, **fields}).status_code, 400)
