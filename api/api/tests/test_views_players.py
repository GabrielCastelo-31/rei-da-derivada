import io
import random
from unittest.mock import MagicMock
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Sumula, Event,  Token, Player
from users.models import User
import uuid
from django.core.files.uploadedfile import UploadedFile, SimpleUploadedFile
from django.contrib.auth.models import Group
from ..permissions import assign_permissions
from guardian.shortcuts import remove_perm, get_perms
from decouple import config
import pandas as pd
XLSX_PATH = config("XLSX_FILE_PATH")
CSV_PATH = config("CSV_FILE_PATH")


class PlayersViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def remove_permissions(self, user, event):
        perms = get_perms(user, event)
        for perm in perms:
            remove_perm(perm, user, event)

    def generate_random_name(self):
        names = ['João', 'José', 'Pedro', 'Paulo', 'Lucas', 'Mário', 'Luiz']
        return names[random.randint(0, 6)]

    def setupUser(self):
        self.admin = User.objects.create(
            username='admin', email=f'{uuid.uuid4()}@gmail.com', first_name='Admin', last_name='Admin')
        self.user_staff_manager = User.objects.create(
            username='staff_manager', email=f'{uuid.uuid4()}@gmail.com', first_name='Staff', last_name='Manager')
        self.user_staff_member = User.objects.create(
            username='staff_member', email=f'{uuid.uuid4()}@gmail.com', first_name='Staff', last_name='Member')
        self.user = User.objects.create(
            username=self.create_unique_username(), email=f'{uuid.uuid4()}@gmail.com', first_name=self.generate_random_name(), last_name=self.generate_random_name())
        self.user2 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name=self.generate_random_name(), last_name=self.generate_random_name())

        self.user3 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name=self.generate_random_name(), last_name=self.generate_random_name())

        self.user4 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name=self.generate_random_name(), last_name=self.generate_random_name())

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpPlayers(self):
        self.player = Player.objects.create(
            user=self.user, event=self.event, registration_email=self.create_unique_email())
        self.player2 = Player.objects.create(
            user=self.user2, event=self.event, registration_email=self.create_unique_email())
        self.player3 = Player.objects.create(
            user=self.user3, event=self.event, registration_email=self.create_unique_email())
        self.player4 = Player.objects.create(
            user=self.user4, event=self.event, registration_email=self.create_unique_email())

    def setUpGroup(self):
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.group_event_admin = Group.objects.create(name='event_admin')
        self.group_staff_manager = Group.objects.create(name='staff_manager')
        self.group_staff_member = Group.objects.create(name='staff_member')
        self.group_player = Group.objects.create(name='player')

    def setUpPermissions(self):
        assign_permissions(self.user_staff_manager,
                           self.group_staff_manager, self.event)
        assign_permissions(self.user_staff_member,
                           self.group_staff_member, self.event)
        assign_permissions(self.admin,
                           self.group_event_admin, self.event)
        assign_permissions(self.user, self.group_player, self.event)

    def setUp(self):
        self.setUpEvent()
        self.setupUser()
        self.setUpPlayers()
        self.setUpGroup()
        self.setUpPermissions()
        self.client = APIClient()
        self.url = f"{reverse('api:players')}?event_id={self.event.id}"

    def test_get_all_players(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

        expected_user_ids = [self.user.id,
                             self.user2.id, self.user3.id, self.user4.id]

        returned_user_ids = [player['user']['id'] for player in response.data]
        returned_event_ids = [player['event'] for player in response.data]

        self.assertCountEqual(returned_user_ids, expected_user_ids)
        self.assertTrue(
            all(event_id == self.event.id for event_id in returned_event_ids))

    def test_get_all_players_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_players_without_event_id(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api:players')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data['errors'], 'event_id is required')

    def test_get_all_players_without_permission(self):
        self.remove_permissions(self.user, self.event)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_players_with_invalid_event_id(self):
        self.client.force_authenticate(user=self.admin)
        url = f"{reverse('api:players')}?event_id=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_players_withouth_any_player(self):
        self.client.force_authenticate(user=self.admin)
        Player.objects.all().delete()
        url = f"{reverse('api:players')}?event_id={self.event.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'Nenhum jogador encontrado!')

    def test_post_add_user_to_event(self):
        self.client.force_authenticate(user=self.user_player1)
        data = {"email": self.player.registration_email,
                "players_token": self.event.players_token}
        response = self.client.post(self.url_post, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'Jogador adicionado com sucesso!')
        self.assertEqual(self.player.user, self.user_player1)
        self.assertEqual(self.player.event, self.event)
        perms = get_perms(self.user_player1, self.event)
        self.assertTrue(all(perm in perms for perm in [
                        'view_player_event', 'view_event', 'view_sumula_event', 'view_player_score_event']))

    def test_post_add_user_to_event_without_previous_player(self):
        user = User.objects.create(username=self.create_unique_username(), email=self.create_unique_email(
        ), first_name=self.generate_random_name(), last_name=self.generate_random_name())
        self.client.force_authenticate(user=user)
        data = {"email": self.create_unique_email(),
                "players_token": self.event.players_token}
        response = self.client.post(self.url_post, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'errors': 'Jogador não encontrado!'})
        with self.assertRaises(Player.DoesNotExist):
            Player.objects.get(user=user)

    def test_post_add_user_to_event_without_email(self):
        self.client.force_authenticate(user=self.user_player1)
        data = {"players_token": self.event.players_token}
        response = self.client.post(self.url_post, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_add_user_to_event_without_token(self):
        self.client.force_authenticate(user=self.user_player1)
        data = {"email": self.create_unique_email()}
        response = self.client.post(self.url_post, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_unauthenticated(self):
        data = {"email": self.create_unique_email(),
                "players_token": self.event.players_token}
        response = self.client.post(self.url_post, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        User.objects.all().delete()
        Sumula.objects.all().delete()
        Event.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.data = None


class GetPlayerResultsViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def generate_random_name(self):
        names = ['João', 'José', 'Pedro', 'Paulo', 'Lucas', 'Mário', 'Luiz']
        return names[random.randint(0, 6)]

    def setupUser(self):
        self.user = User.objects.create(
            username=self.create_unique_username(), email=f'{uuid.uuid4()}@gmail.com',
            first_name=self.generate_random_name(), last_name=self.generate_random_name())
        self.user_staff_manager = User.objects.create(
            username='staff_manager', email=f'{uuid.uuid4()}@gmail.com')
        self.user_staff_member = User.objects.create(
            username='staff_member', email=f'{uuid.uuid4()}@gmail.com')
        self.admin = User.objects.create(
            username='admin', email=f'{uuid.uuid4()}@gmail.com')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(
            name='Evento 1', token=self.token, results_published=True)

    def setUpPlayers(self):
        self.player = Player.objects.create(
            user=self.user, event=self.event, registration_email=self.create_unique_email())

    def setUpGroup(self):
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.group_event_admin = Group.objects.create(name='event_admin')
        self.group_staff_manager = Group.objects.create(name='staff_manager')
        self.group_staff_member = Group.objects.create(name='staff_member')
        self.group_player = Group.objects.create(name='player')

    def setUpPermissions(self):
        assign_permissions(self.user_staff_manager,
                           self.group_staff_manager, self.event)
        assign_permissions(self.user_staff_member,
                           self.group_staff_member, self.event)
        assign_permissions(self.admin,
                           self.group_event_admin, self.event)
        assign_permissions(self.user, self.group_player, self.event)

    def setUp(self):
        self.setUpEvent()
        self.setupUser()
        self.setUpPlayers()
        self.setUpGroup()
        self.setUpPermissions()
        self.url = f"{reverse('api:player')}?event_id={self.event.id}"
        self.client = APIClient()

    def remove_permissions(self, user, event):
        perms = get_perms(user, event)
        for perm in perms:
            remove_perm(perm, user, event)

    def test_get_player(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.player.id,
            'total_score': self.player.total_score,
            'full_name': self.player.full_name,
            'social_name': self.player.social_name,
        })

    def test_get_player_without_event_id(self):
        self.client.force_authenticate(user=self.user)
        url = f"{reverse('api:player')}?event_id="
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['event_id é obrigatório!']"})

    def test_get_player_with_invalid_event_id(self):
        self.client.force_authenticate(user=self.user)
        url = f"{reverse('api:player')}?event_id=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['Evento não encontrado!']"})

    def test_get_player_without_permission(self):
        self.remove_permissions(self.user, self.event)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_player_unauthenticated(self):
        url = reverse('api:player')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_player_without_player_associated(self):
        self.client.force_authenticate(user=self.admin)
        Player.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,  {'errors': 'Jogador não encontrado!'})

    def test_get_player_results_published_false(self):
        self.event.results_published = False
        self.event.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data, 'Resultados não publicados!')

    def tearDown(self):
        User.objects.all().delete()
        Sumula.objects.all().delete()
        Event.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.client = None


class AddPlayersViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def generate_random_name(self):
        names = ['João', 'José', 'Pedro', 'Paulo', 'Lucas', 'Mário', 'Luiz']
        return names[random.randint(0, 6)]

    def setupUser(self):
        self.admin = User.objects.create(
            username='admin', email=f'{uuid.uuid4()}@gmail.com', first_name='Admin', last_name='Admin')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.group_event_admin = Group.objects.create(name='event_admin')
        self.group_staff_manager = Group.objects.create(name='staff_manager')
        self.group_staff_member = Group.objects.create(name='staff_member')
        self.group_player = Group.objects.create(name='player')

    def setUpPermissions(self):
        assign_permissions(self.admin,
                           self.group_event_admin, self.event)

    def setUpFiles(self):
        # Setup Excel file
        self.excel_file = open(XLSX_PATH, 'rb')
        self.excel_content = self.excel_file.read()
        self.excel_uploaded_file = SimpleUploadedFile(
            "Exemplo.xlsx", self.excel_content, content_type="multipart/form-data")
        # Setup CSV file
        self.csv_file = open(
            '/usr/src/api/config/files_tests/excel/Exemplo.csv', 'r')
        self.csv_content = self.csv_file.read()
        self.csv_uploaded_file = SimpleUploadedFile(
            "Exemplo.csv", self.csv_content.encode('utf-8'), content_type="multipart/form-data")

    def setUpUrl(self):
        self.url_csv = f"{reverse('api:upload', kwargs={'filename': 'participantes.csv'})}?event_id={self.event.id}"
        self.url_excel = f"{reverse('api:upload', kwargs={'filename': 'participantes.xlsx'})}?event_id={self.event.id}"

    def remove_permissions(self):
        perm = get_perms(self.admin, self.event)
        for p in perm:
            remove_perm(p, self.admin, self.event)

    def setUp(self):
        self.setUpEvent()
        self.setupUser()
        self.setUpGroup()
        self.setUpPermissions()
        self.setUpFiles()
        self.setUpUrl()
        self.client = APIClient()

    def test_add_players_csv(self):
        self.client.force_authenticate(user=self.admin)

        data = {'file': self.csv_uploaded_file}

        response = self.client.post(self.url_csv, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'Jogadores adicionados com sucesso!')

        players = Player.objects.filter(event=self.event)
        self.assertEqual(players.count(), 10)

    def test_add_players_excel(self):
        self.client.force_authenticate(user=self.admin)
        data = {'file': self.excel_uploaded_file}
        response = self.client.post(self.url_excel, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'Jogadores adicionados com sucesso!')
        players = Player.objects.filter(event=self.event)
        self.assertEqual(players.count(), 10)

    def test_add_players_unauthenticated(self):
        data = {'file': self.csv_uploaded_file}
        response = self.client.post(self.url_csv, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_players_without_permission(self):
        self.remove_permissions()
        self.client.force_authenticate(user=self.admin)
        data = {'file': self.csv_uploaded_file}
        response = self.client.post(self.url_csv, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_players_without_event_id(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api:upload', kwargs={'filename': 'participantes.csv'})
        response = self.client.post(url, {'file': self.csv_uploaded_file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['Dados inválidos!']"})

    def test_add_players_with_invalid_event_id(self):
        self.client.force_authenticate(user=self.admin)
        url = f"{reverse('api:upload', kwargs={'filename': 'participantes.csv'})}?event_id=100"
        response = self.client.post(url, {'file': self.csv_uploaded_file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['Evento não encontrado!']"})

    def tearDown(self):
        User.objects.all().delete()
        Event.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.data = None
        self.excel_file.close()


class PublishPlayersResultsViewTestCase(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def remove_permissions(self, user, event):
        perms = get_perms(user, event)
        for perm in perms:
            remove_perm(perm, user, event)

    def setUpUser(self):
        self.admin = User.objects.create(username='admin', email=self.create_unique_email(
        ), first_name='Admin', last_name='Admin')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.group_event_admin = Group.objects.create(name='event_admin')
        self.group_staff_manager = Group.objects.create(name='staff_manager')
        self.group_staff_member = Group.objects.create(name='staff_member')
        self.group_player = Group.objects.create(name='player')

    def setUpPermissions(self):
        assign_permissions(self.admin,
                           self.group_event_admin, self.event)

    def setUp(self):
        self.setUpUser()
        self.setUpEvent()
        self.setUpGroup()
        self.setUpPermissions()
        self.url = f"{reverse('api:publish-results')}?event_id={self.event.id}"
        self.client = APIClient()

    def test_publish_results(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'Resultados publicados com sucesso!')
        self.event.refresh_from_db()
        self.assertEqual(self.event.results_published, True)

    def test_publish_results_unauthenticated(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publish_results_without_permission(self):
        self.remove_permissions(self.admin, self.event)
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.event.refresh_from_db()
        self.assertEqual(self.event.results_published, False)

    def test_publish_results_without_event_id(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api:publish-results')
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['Dados inválidos!']"})
        self.event.refresh_from_db()
        self.assertEqual(self.event.results_published, False)

    def test_publish_results_with_invalid_event_id(self):
        self.client.force_authenticate(user=self.admin)
        url = f"{reverse('api:publish-results')}?event_id=100"
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['Evento não encontrado!']"})
        self.event.refresh_from_db()
        self.assertEqual(self.event.results_published, False)

    def tearDown(self):
        User.objects.all().delete()
        Event.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.data = None


class Top4PlayersViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpUser(self):
        self.user0 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email())
        self.user1 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email())
        self.user2 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email())
        self.user3 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email())
        self.user4 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email())

    def setUpPlayer(self):
        self.player0 = Player.objects.create(
            event=self.event, user=self.user0, total_score=0, registration_email=self.create_unique_email())
        self.player1 = Player.objects.create(
            event=self.event, user=self.user1, total_score=10, registration_email=self.create_unique_email())
        self.player2 = Player.objects.create(
            event=self.event, user=self.user2, total_score=20, registration_email=self.create_unique_email())
        self.player3 = Player.objects.create(
            event=self.event, user=self.user3, total_score=30, registration_email=self.create_unique_email())
        self.player4 = Player.objects.create(
            event=self.event, user=self.user4, total_score=40, registration_email=self.create_unique_email())

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(
            name='Evento 1', token=self.token, results_published=True)

    def setUpGroup(self):
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.group_player = Group.objects.create(name='player')

    def setUpPermissions(self):
        assign_permissions(self.user0, self.group_player, self.event)

    def setUp(self):
        self.setUpUser()
        self.setUpEvent()
        self.setUpPlayer()
        self.setUpGroup()
        self.setUpPermissions()
        self.url = reverse('api:top4')

    def test_get_top_4_players(self):

        self.client.force_authenticate(user=self.user0)
        response = self.client.get(self.url, {'event_id': self.event.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

        expected_player_ids = [self.player4.id,
                               self.player3.id, self.player2.id, self.player1.id]
        returned_player_ids = [player['id'] for player in response.data]

        self.assertEqual(returned_player_ids, expected_player_ids)

    def test_get_top_4_players_unauthenticated(self):
        response = self.client.get(self.url, {'event_id': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_top_4_players_without_event_id(self):
        self.client.force_authenticate(user=self.user0)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'errors': "['Dados inválidos!']"})

    def test_get_top_4_players_with_invalid_event_id(self):
        self.client.force_authenticate(user=self.user0)
        response = self.client.get(self.url, {'event_id': 100})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['Evento não encontrado!']"})

    def tearDown(self) -> None:
        User.objects.all().delete()
        Event.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
