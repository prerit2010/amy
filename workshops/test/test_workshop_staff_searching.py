import unittest

from django.core.urlresolvers import reverse

from .base import TestBase
from ..models import Task, Role, Event, Tag, Host


class TestLocateWorkshopStaff(TestBase):
    '''Test cases for locating workshop staff.'''

    def setUp(self):
        super().setUp()
        self._setUpTags()
        self._setUpRoles()
        self._setUpUsersAndLogin()

    def test_non_instructors_and_instructors_returned_by_search(self):
        """Ensure search returns everyone with defined airport."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport_1': self.airport_0_0.pk, 'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)

        # instructors
        self.assertIn(self.hermione, response.context['persons'])
        self.assertIn(self.harry, response.context['persons'])
        self.assertIn(self.ron, response.context['persons'])
        # non-instructors
        self.assertIn(self.spiderman, response.context['persons'])
        self.assertIn(self.ironman, response.context['persons'])
        self.assertIn(self.blackwidow, response.context['persons'])

    def test_match_on_one_skill(self):
        """Ensure people with correct skill are returned."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport_1': self.airport_50_100.pk, 'lessons': [self.git.pk],
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)
        # lessons
        self.assertIn(self.git, response.context['lessons'])

        # instructors
        self.assertIn(self.hermione, response.context['persons'])
        self.assertNotIn(self.harry, response.context['persons'])
        self.assertIn(self.ron, response.context['persons'])
        # non-instructors
        self.assertNotIn(self.spiderman, response.context['persons'])
        self.assertNotIn(self.ironman, response.context['persons'])
        self.assertNotIn(self.blackwidow, response.context['persons'])

    def test_match_instructors_on_two_skills(self):
        """Ensure people with correct skills are returned."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport_1': self.airport_50_100.pk,
             'lessons': [self.git.pk, self.sql.pk],
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)
        # lessons
        self.assertIn(self.git, response.context['lessons'])
        self.assertIn(self.sql, response.context['lessons'])

        # instructors
        self.assertIn(self.hermione, response.context['persons'])
        self.assertNotIn(self.harry, response.context['persons'])
        self.assertNotIn(self.ron, response.context['persons'])
        # non-instructors
        self.assertNotIn(self.spiderman, response.context['persons'])
        self.assertNotIn(self.ironman, response.context['persons'])
        self.assertNotIn(self.blackwidow, response.context['persons'])

    def test_match_by_country(self):
        """Ensure people with airports in Bulgaria are returned."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'country': ['BG'], 'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)

        # instructors
        self.assertNotIn(self.hermione, response.context['persons'])
        self.assertIn(self.harry, response.context['persons'])
        self.assertNotIn(self.ron, response.context['persons'])
        # non-instructors
        self.assertNotIn(self.spiderman, response.context['persons'])
        self.assertNotIn(self.ironman, response.context['persons'])
        self.assertIn(self.blackwidow, response.context['persons'])

    def test_match_by_multiple_countries(self):
        """Ensure people with airports in Albania and Bulgaria are returned."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'country': ['AL', 'BG'], 'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)

        # instructors
        self.assertIn(self.hermione, response.context['persons'])
        self.assertIn(self.harry, response.context['persons'])
        self.assertNotIn(self.ron, response.context['persons'])
        # non-instructors
        self.assertNotIn(self.spiderman, response.context['persons'])
        self.assertNotIn(self.ironman, response.context['persons'])
        self.assertIn(self.blackwidow, response.context['persons'])

    def test_match_gender(self):
        """Ensure only people with specific gender are returned."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport': self.airport_0_0.pk, 'gender': 'F', 'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)

        # instructors
        self.assertIn(self.hermione, response.context['persons'])
        self.assertNotIn(self.harry, response.context['persons'])
        self.assertNotIn(self.ron, response.context['persons'])
        # non-instructors
        self.assertNotIn(self.spiderman, response.context['persons'])
        self.assertNotIn(self.ironman, response.context['persons'])
        self.assertIn(self.blackwidow, response.context['persons'])

    def test_instructor_badges(self):
        """Ensure people with instructor badges are returned by search."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport': self.airport_0_0.pk,
             'instructor_badges': ['swc-instructor', 'dc-instructor'],
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)

        # instructors
        self.assertIn(self.hermione, response.context['persons'])
        self.assertIn(self.harry, response.context['persons'])
        # Ron doesn't have a DC badge
        self.assertNotIn(self.ron, response.context['persons'])
        # non-instructors
        self.assertNotIn(self.spiderman, response.context['persons'])
        self.assertNotIn(self.ironman, response.context['persons'])
        self.assertNotIn(self.blackwidow, response.context['persons'])

    def test_match_on_one_language(self):
        """Ensure people with one particular language preference
        are returned by search."""
        # prepare langauges
        self._setUpLanguages()
        # Ron can communicate in English
        self.ron.languages.add(self.english)
        self.ron.save()
        # Harry can communicate in French
        self.harry.languages.add(self.french)
        self.harry.save()

        response = self.client.get(
            reverse('workshop_staff'),
            {'languages_1': [self.french.pk,],
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.harry, response.context['persons'])
        self.assertNotIn(self.ron, response.context['persons'])

    def test_match_on_many_language(self):
        """Ensure people with a set of language preferences
        are returned by search."""
        # prepare langauges
        self._setUpLanguages()
        # Ron can communicate in many languages
        self.ron.languages.add(self.english, self.french)
        self.ron.save()
        # Harry is mono-lingual
        self.harry.languages.add(self.french)
        self.harry.save()

        response = self.client.get(
            reverse('workshop_staff'),
            {'languages_1': [self.english.pk, self.french.pk],
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.ron, response.context['persons'])
        self.assertNotIn(self.harry, response.context['persons'])

    def test_roles(self):
        """Ensure people with at least one helper/organizer roles are returned
        by search."""
        # prepare events and tasks
        self._setUpEvents()
        helper_role = Role.objects.get(name='helper')
        organizer_role = Role.objects.get(name='organizer')

        Task.objects.create(role=helper_role, person=self.spiderman,
                            event=Event.objects.first())
        Task.objects.create(role=organizer_role, person=self.blackwidow,
                            event=Event.objects.first())

        response = self.client.get(
            reverse('workshop_staff'),
            {'airport': self.airport_0_0.pk,
             'was_helper': 'on',
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['persons']), [self.spiderman])

        response = self.client.get(
            reverse('workshop_staff'),
            {'airport': self.airport_0_0.pk,
             'was_organizer': 'on',
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['persons']), [self.blackwidow])

    def test_form_logic(self):
        """Check if logic preventing searching from multiple fields,
        except lat+lng pair, and allowing searching from no location field,
        works."""
        test_vectors = [
            (True, {'latitude': 1, 'longitude': 2}),
            (True, dict()),
            (False, {'latitude': 1}),
            (False, {'longitude': 1, 'country': ['BG']}),
            (False, {'latitude': 1, 'longitude': 2, 'country': ['BG']}),
            (False, {'latitude': 1, 'longitude': 2, 'country': ['BG'],
                     'airport': self.airport_0_0.pk}),
        ]

        for form_pass, data in test_vectors:
            with self.subTest(data=data):
                params = dict(submit='Submit')
                params.update(data)
                rv = self.client.get(reverse('workshop_staff'), params)
                form = rv.context['form']
                self.assertEqual(form.is_valid(), form_pass, form.errors)

    def test_searching_trainees(self):
        """Make sure finding trainees works."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport': self.airport_0_0.pk,
             'is_in_progress_trainee': 'on',
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['persons']), [])

        TTT = Tag.objects.get(name='TTT')
        stalled = Tag.objects.get(name='stalled')
        e1 = Event.objects.create(slug='TTT-event', host=Host.objects.first())
        e1.tags = [TTT]
        e2 = Event.objects.create(slug='stalled-TTT-event',
                                  host=Host.objects.first())
        e2.tags = [TTT, stalled]

        learner = Role.objects.get(name='learner')
        # Ron is an instructor, so he should not be available as a trainee
        Task.objects.create(person=self.ron, event=e1, role=learner)
        Task.objects.create(person=self.ron, event=e2, role=learner)
        # Black Widow, on the other hand, is now practising to become certified
        # SWC instructor!
        Task.objects.create(person=self.blackwidow, event=e1, role=learner)
        # Spiderman tried to became an instructor, but hasn't finished it yet
        Task.objects.create(person=self.spiderman, event=e2, role=learner)

        # repeat the query
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport': self.airport_0_0.pk,
             'is_in_progress_trainee': 'on',
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['persons']), [self.blackwidow])

    @unittest.expectedFailure
    def test_searching_complicated_trainee(self):
        """Ensure person who took part in one stalled TTT event and one
        non-stalled TTT event is correctly marked as in-progress trainee.

        This test should fail because Django ORM fails with annotations.
        See https://github.com/swcarpentry/amy/pull/776#discussion_r63953993
        and https://github.com/swcarpentry/amy/issues/804."""
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport': self.airport_0_0.pk,
             'is_in_progress_trainee': 'on',
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['persons']), [])

        TTT = Tag.objects.get(name='TTT')
        stalled = Tag.objects.get(name='stalled')
        e1 = Event.objects.create(slug='TTT-event', host=Host.objects.first())
        e1.tags = [TTT]
        e2 = Event.objects.create(slug='stalled-TTT-event',
                                  host=Host.objects.first())
        e2.tags = [TTT, stalled]

        learner = Role.objects.get(name='learner')

        # Ron is an instructor, so he should not be available as a trainee
        Task.objects.create(person=self.ron, event=e1, role=learner)
        Task.objects.create(person=self.ron, event=e2, role=learner)
        # Black Widow, on the other hand, is now practising to become certified
        # SWC instructor!
        Task.objects.create(person=self.blackwidow, event=e1, role=learner)
        # Ironman tried to became an instructor via one event, but didn't
        # finish and now is taking part in another TTT event
        Task.objects.create(person=self.ironman, event=e1, role=learner)
        Task.objects.create(person=self.ironman, event=e2, role=learner)

        # repeat the query
        response = self.client.get(
            reverse('workshop_staff'),
            {'airport': self.airport_0_0.pk,
             'is_in_progress_trainee': 'on',
             'submit': 'Submit'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ironman.pk, response.context['trainees'])
        self.assertEqual(list(response.context['persons']),
                         [self.blackwidow, self.ironman])
