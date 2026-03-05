from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.kitchens.models import Kitchen
from apps.menu.models import Category, Item
from apps.orders.models import OrderItem, OrderSession
from apps.restaurants.models import Restaurant, Branch, Table


class PermissionsAndOrderFlowTests(APITestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            username='super', email='super@test.com', password='pass1234', role='superadmin'
        )
        self.owner = User.objects.create_user(
            username='owner', email='owner@test.com', password='pass1234', role='owner'
        )
        self.owner2 = User.objects.create_user(
            username='owner2', email='owner2@test.com', password='pass1234', role='owner'
        )

        self.restaurant = Restaurant.objects.create(name='R1', owner=self.owner)
        self.restaurant2 = Restaurant.objects.create(name='R2', owner=self.owner2)

        self.owner.restaurant = self.restaurant
        self.owner.save()
        self.owner2.restaurant = self.restaurant2
        self.owner2.save()

        self.branch = Branch.objects.create(
            restaurant=self.restaurant, name='B1', location='L1', branch_number=1
        )
        self.branch2 = Branch.objects.create(
            restaurant=self.restaurant2, name='B2', location='L2', branch_number=1
        )

        self.branch_manager = User.objects.create_user(
            username='bm', email='bm@test.com', password='pass1234', role='branch_manager', branch=self.branch
        )
        self.waiter = User.objects.create_user(
            username='waiter', email='waiter@test.com', password='pass1234', role='waiter', branch=self.branch
        )
        self.waiter_kitchen_only = User.objects.create_user(
            username='waiterk', email='waiterk@test.com', password='pass1234', role='waiter'
        )
        self.customer = User.objects.create_user(
            username='customer', email='customer@test.com', password='pass1234', role='customer'
        )

        self.kitchen = Kitchen.objects.create(name='Main Kitchen', branch=self.branch)
        self.kitchen2 = Kitchen.objects.create(name='Other Kitchen', branch=self.branch2)

        self.waiter_kitchen_only.kitchen = self.kitchen
        self.waiter_kitchen_only.save()

        self.kitchen_manager = User.objects.create_user(
            username='km', email='km@test.com', password='pass1234', role='kitchen_manager', kitchen=self.kitchen
        )
        self.chef = User.objects.create_user(
            username='chef', email='chef@test.com', password='pass1234', role='chef', kitchen=self.kitchen
        )

        self.table = Table.objects.create(branch=self.branch, number=1, seats=4)
        self.category = Category.objects.create(name='Hot', kitchen=self.kitchen)
        self.item = Item.objects.create(name='Soup', price='12.50', category=self.category)

    def test_owner_cannot_create_branch_for_other_restaurant(self):
        self.client.force_authenticate(self.owner)
        url = '/api/restaurants/branches/'
        payload = {
            'restaurant': self.restaurant2.id,
            'name': 'Illegal Branch',
            'location': 'X'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_branch_manager_can_create_table_outside_branch(self):
        self.client.force_authenticate(self.branch_manager)
        url = '/api/restaurants/tables/'
        payload = {
            'branch': self.branch2.id,
            'number': 9,
            'seats': 4,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_branch_manager_cannot_create_kitchen_outside_branch(self):
        self.client.force_authenticate(self.branch_manager)
        url = '/api/kitchens/kitchens/'
        payload = {
            'name': 'Illegal Kitchen',
            'branch': self.branch2.id,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_waiter_order_flow_end_to_end_with_chef_transitions(self):
        self.client.force_authenticate(self.waiter)

        session_resp = self.client.post('/api/orders/sessions/', {'table': self.table.id}, format='json')
        self.assertIn(session_resp.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        session_id = session_resp.data['id']

        item_resp = self.client.post(
            '/api/orders/items/',
            {
                'order_session': session_id,
                'item': self.item.id,
                'quantity': 2,
                'notes': 'Less salt'
            },
            format='json'
        )
        self.assertEqual(item_resp.status_code, status.HTTP_201_CREATED)
        order_item_id = item_resp.data['id']

        order_item = OrderItem.objects.get(id=order_item_id)
        self.assertEqual(order_item.price_at_order_time, Decimal('12.50'))
        self.assertEqual(order_item.status, 'pending')

        self.client.force_authenticate(self.chef)
        for expected in ['accepted', 'cooking', 'ready', 'served']:
            update_resp = self.client.patch(
                f'/api/orders/items/{order_item_id}/',
                {'status': expected},
                format='json'
            )
            self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        order_item.refresh_from_db()
        self.assertEqual(order_item.status, 'served')

    def test_chef_cannot_create_order_item(self):
        session = OrderSession.objects.create(table=self.table)
        self.client.force_authenticate(self.chef)
        response = self.client.post(
            '/api/orders/items/',
            {
                'order_session': str(session.id),
                'item': self.item.id,
                'quantity': 1,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



    def test_waiter_cannot_create_table_outside_effective_scope(self):
        self.client.force_authenticate(self.waiter)
        response = self.client.post(
            '/api/restaurants/tables/',
            {'branch': self.branch2.id, 'number': 10, 'seats': 4},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_waiter_with_kitchen_only_can_open_session_in_kitchen_branch(self):
        self.client.force_authenticate(self.waiter_kitchen_only)
        response = self.client.post('/api/orders/sessions/', {'table': self.table.id}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_waiter_can_open_session_using_table_number_not_pk(self):
        self.client.force_authenticate(self.waiter)
        response = self.client.post('/api/orders/sessions/', {'table': self.table.number}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        self.assertEqual(response.data['table'], self.table.id)

    def test_anonymous_can_create_order_item_with_valid_session_password(self):
        session = OrderSession.objects.create(table=self.table)

        response = self.client.post(
            '/api/orders/items/',
            {
                'order_session': str(session.id),
                'item': self.item.id,
                'quantity': 3,
                'session_password': session.session_password,
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = OrderItem.objects.get(id=response.data['id'])
        self.assertEqual(created.quantity, 3)
        session.refresh_from_db()
        self.assertEqual(session.total_amount, Decimal('37.50'))

    def test_anonymous_cannot_create_order_item_with_invalid_session_password(self):
        session = OrderSession.objects.create(table=self.table)

        response = self.client.post(
            '/api/orders/items/',
            {
                'order_session': str(session.id),
                'item': self.item.id,
                'quantity': 1,
                'session_password': '000000',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_customer_can_open_session_for_table(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post('/api/orders/sessions/', {'table': self.table.id}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_kitchen_manager_cannot_open_session(self):
        self.client.force_authenticate(self.kitchen_manager)
        response = self.client.post('/api/orders/sessions/', {'table': self.table.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
