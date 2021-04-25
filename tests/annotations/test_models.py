from django.test import TestCase

from pepysdiary.annotations.factories import EntryAnnotationFactory
from pepysdiary.annotations.models import Annotation
from pepysdiary.common.utilities import make_datetime
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.membership.factories import PersonFactory


class AnnotationTestCase(TestCase):
    def test_objects(self):
        "It should include not public and removed Annotations"

        visible_annotation = EntryAnnotationFactory(is_public=True, is_removed=False)
        not_public_annotation = EntryAnnotationFactory(
            is_public=False, is_removed=False
        )
        removed_annotation = EntryAnnotationFactory(is_public=True, is_removed=True)
        not_public_and_removed_annotation = EntryAnnotationFactory(
            is_public=False, is_removed=True
        )

        annotations = Annotation.objects.all()

        self.assertEqual(len(annotations), 4)
        self.assertIn(visible_annotation, annotations)
        self.assertIn(not_public_annotation, annotations)
        self.assertIn(removed_annotation, annotations)
        self.assertIn(not_public_and_removed_annotation, annotations)

    def test_visible_objects(self):
        "It should only include public and not removed Annotations"
        visible_annotation = EntryAnnotationFactory(is_public=True, is_removed=False)
        EntryAnnotationFactory(is_public=False, is_removed=False)
        EntryAnnotationFactory(is_public=True, is_removed=True)
        EntryAnnotationFactory(is_public=False, is_removed=True)

        annotations = Annotation.visible_objects.all()

        self.assertEqual(len(annotations), 1)
        self.assertIn(visible_annotation, annotations)

    def test_ordering(self):
        "They should be ordered by submit_date ascending"
        annotation_1 = EntryAnnotationFactory(
            submit_date=make_datetime("2021-04-10 12:00:00")
        )
        annotation_2 = EntryAnnotationFactory(
            submit_date=make_datetime("2021-04-09 12:00:00")
        )
        annotation_3 = EntryAnnotationFactory(
            submit_date=make_datetime("2021-04-11 12:00:00")
        )

        annotations = Annotation.objects.all()
        self.assertEqual(annotations[0], annotation_2)
        self.assertEqual(annotations[1], annotation_1)
        self.assertEqual(annotations[2], annotation_3)

    def test_strips_html_tags(self):
        "HTML tags should be stripped on save"
        annotation = EntryAnnotationFactory(
            comment='<b>Bold</b> <a href="http://example.com">Link</a> OK?'
        )
        self.assertEqual(annotation.comment, "Bold Link OK?")

    def test_sets_parent_comment_data(self):
        "It should set the parent object's Annotation-related data on save"
        entry = EntryFactory()
        annotation = EntryAnnotationFactory(content_object=entry)

        entry.refresh_from_db()

        self.assertEqual(entry.comment_count, 1)
        self.assertEqual(entry.last_comment_time, annotation.submit_date)

    def test_parent_comment_data_ignores_non_visible_annotations(self):
        "comment_count and last_comment_time should only include visible annotations"
        entry = EntryFactory()

        # This early annotation is the only one that should be included:
        annotation = EntryAnnotationFactory(
            content_object=entry,
            is_public=True,
            is_removed=False,
            submit_date=make_datetime(("2021-04-09 12:00:00")),
        )

        # None of these should be included:
        EntryAnnotationFactory(
            content_object=entry,
            is_public=False,
            is_removed=False,
            submit_date=make_datetime("2021-04-10 12:00:00"),
        )
        EntryAnnotationFactory(
            content_object=entry,
            is_public=True,
            is_removed=True,
            submit_date=make_datetime("2021-04-11 12:00:00"),
        )
        EntryAnnotationFactory(
            content_object=entry,
            is_public=False,
            is_removed=True,
            submit_date=make_datetime("2021-04-12 12:00:00"),
        )

        entry.refresh_from_db()

        self.assertEqual(entry.comment_count, 1)
        self.assertEqual(entry.last_comment_time, annotation.submit_date)

    def test_parent_comment_data_on_delete(self):
        "When deleting an annotation, the parent's comment data should be updated"
        entry = EntryFactory()

        # This early annotation is the only one that should be included:
        annotation_1 = EntryAnnotationFactory(
            content_object=entry,
            is_public=True,
            is_removed=False,
            submit_date=make_datetime(("2021-04-09 12:00:00")),
        )
        annotation_2 = EntryAnnotationFactory(
            content_object=entry,
            is_public=True,
            is_removed=False,
            submit_date=make_datetime(("2021-04-10 12:00:00")),
        )
        annotation_2.delete()

        entry.refresh_from_db()

        self.assertEqual(entry.comment_count, 1)
        self.assertEqual(entry.last_comment_time, annotation_1.submit_date)

    def test_set_users_first_comment_date_first(self):
        "If this is the user's first annotation, we set their first_comment_date"
        person = PersonFactory(first_comment_date=None)
        annotation = EntryAnnotationFactory(user=person)

        person.refresh_from_db()

        self.assertEqual(person.first_comment_date, annotation.submit_date)

    def test_set_user_first_comment_date_second(self):
        "If this isn't the user's first annotation, don't set first_comment_date"
        person = PersonFactory(first_comment_date=None)
        annotation_1 = EntryAnnotationFactory(
            user=person, submit_date=make_datetime("2021-04-10 12:00:00")
        )
        EntryAnnotationFactory(
            user=person, submit_date=make_datetime("2021-04-11 12:00:00")
        )

        person.refresh_from_db()

        self.assertEqual(person.first_comment_date, annotation_1.submit_date)

    def test_set_user_first_coment_date_earlier(self):
        "If annotation is earlier than the user's first_comment_date, use that"
        person = PersonFactory(first_comment_date=None)
        EntryAnnotationFactory(
            user=person, submit_date=make_datetime("2021-04-10 12:00:00")
        )
        annotation_2 = EntryAnnotationFactory(
            user=person, submit_date=make_datetime("2021-04-09 12:00:00")
        )

        person.refresh_from_db()

        self.assertEqual(person.first_comment_date, annotation_2.submit_date)

    def test_set_user_first_comment_date_visible_only(self):
        "Setting the user's first_comment_date only happens if annotation is visible"
        entry = EntryFactory()
        person = PersonFactory(first_comment_date=None)

        # None of these should be included:
        EntryAnnotationFactory(
            content_object=entry,
            is_public=False,
            is_removed=False,
            submit_date=make_datetime("2021-04-09 12:00:00"),
        )
        EntryAnnotationFactory(
            content_object=entry,
            is_public=True,
            is_removed=True,
            submit_date=make_datetime("2021-04-10 12:00:00"),
        )
        EntryAnnotationFactory(
            content_object=entry,
            is_public=False,
            is_removed=True,
            submit_date=make_datetime("2021-04-11 12:00:00"),
        )

        # This early annotation is the only one that should be included:
        annotation = EntryAnnotationFactory(
            user=person,
            content_object=entry,
            is_public=True,
            is_removed=False,
            submit_date=make_datetime(("2021-04-12 12:00:00")),
        )

        person.refresh_from_db()

        self.assertEqual(person.first_comment_date, annotation.submit_date)

    def test_get_user_name(self):
        "It should return the user_name"
        person = PersonFactory(name="Terry")
        annotation = EntryAnnotationFactory(user=person, user_name="Bob Ferris")
        self.assertEqual(annotation.get_user_name(), "Bob Ferris")

    def test_get_user_email_from_object(self):
        "It should return the user object's email, if any"
        person = PersonFactory(email="terry@example.org")
        annotation = EntryAnnotationFactory(user=person, user_email="bob@example.org")
        self.assertEqual(annotation.get_user_email(), "terry@example.org")

    def test_get_user_email_from_annotation(self):
        "It should return the email from the annotation if there's no user object"
        annotation = EntryAnnotationFactory(user=None, user_email="bob@example.org")
        self.assertEqual(annotation.get_user_email(), "bob@example.org")

    def test_get_user_url_from_object(self):
        "It should return the user object's url, if any"
        person = PersonFactory(url="http://example.org")
        annotation = EntryAnnotationFactory(user=person, user_url="http://foo.com")
        self.assertEqual(annotation.get_user_url(), "http://example.org")

    def test_get_user_url_from_annotation(self):
        "It should return the url from the annotation if there's no user object"
        annotation = EntryAnnotationFactory(user=None, user_url="http://foo.com")
        self.assertEqual(annotation.get_user_url(), "http://foo.com")
