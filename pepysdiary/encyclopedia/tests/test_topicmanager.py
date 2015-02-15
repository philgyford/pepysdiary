# coding: utf-8
from pepysdiary.common.tests.test_base import PepysdiaryTestCase
from pepysdiary.encyclopedia.models import Topic


class TopicManagerTestCase(PepysdiaryTestCase):
    """
    So far, just tests TopicManager.make_order_title().
    """

    # NOT PEOPLE.

    def test_make_order_title_unchanged(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Ale, buttered', is_person=False),
            'Ale, buttered')

    def test_make_order_title_the(self):
        self.assertEqual(Topic.objects.make_order_title(
            'The Royal Prince', is_person=False),
            'Royal Prince, The')

    def test_make_order_title_the_fail(self):
        self.assertNotEqual(Topic.objects.make_order_title(
            'The Royal Prince', is_person=False),
            'The Royal Prince')

    def test_make_order_title_the_parentheses(self):
        self.assertEqual(Topic.objects.make_order_title(
            'The Alchemist (Ben Jonson)', is_person=False),
            'Alchemist, The (Ben Jonson)')

    # PEOPLE THAT NEED CHANGING.

    def test_make_order_title_name(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Thomas Agar', is_person=True),
            'Agar, Thomas')

    def test_make_order_title_name_parentheses(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Sidney Smythe (1st Lord Smythe)', is_person=True),
            'Smythe, Sidney (1st Lord Smythe)')

    def test_make_order_title_name_capt(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Capt. Henry Terne', is_person=True),
            'Terne, Capt. Henry')

    def test_make_order_title_name_mr(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Mr Hazard', is_person=True),
            'Hazard, Mr')

    def test_make_order_title_name_mrs(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Mrs Andrews', is_person=True),
            'Andrews, Mrs')

    def test_make_order_title_name_middle(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Johann Heinrich Alstead', is_person=True),
            'Alstead, Johann Heinrich')

    def test_make_order_title_name_d(self):
        self.assertEqual(Topic.objects.make_order_title(
            "Monsieur d'Esquier", is_person=True),
            "Esquier, Monsieur d'")

    def test_make_order_title_name_de(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Adriaen de Haes', is_person=True),
            'Haes, Adriaen de')

    def test_make_order_title_name_de_parentheses(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Jan de Witt (Grand Pensionary of Holland)', is_person=True),
            'Witt, Jan de (Grand Pensionary of Holland)')

    def test_make_order_title_name_de_la(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Peter de la Roche', is_person=True),
            'Roche, Peter de la')

    def test_make_order_title_name_du(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Monsieur du Prat', is_person=True),
            'Prat, Monsieur du')

    def test_make_order_title_name_of(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Catherine of Braganza (Queen)', is_person=True),
            'Braganza, Catherine of (Queen)')

    def test_make_order_title_name_van(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Michiel van Gogh (Dutch Ambassador, 1664-5)', is_person=True),
            'Gogh, Michiel van (Dutch Ambassador, 1664-5)')

    def test_make_order_title_name_majgenaldsir(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Maj.-Gen. Ald. Sir Richard Browne', is_person=True),
            'Browne, Maj.-Gen. Ald. Sir Richard')

    def test_make_order_title_name_dr_single(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Dr Waldegrave', is_person=True),
            'Waldegrave, Dr')

    def test_make_order_title_name_comte_d(self):
        self.assertEqual(Topic.objects.make_order_title(
            "Godefroy, Comte d'Estrades", is_person=True),
            "Godefroy, Comte d'Estrades")

    def test_make_order_title_name_al(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Abdallah al-Ghailan ("Guiland", "Gayland")', is_person=True),
            'Ghailan, Abdallah al- ("Guiland", "Gayland")')

    def test_make_order_title_name_mr_parentheses(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Mr Butler (Mons. L\'impertinent)', is_person=True),
            'Butler, Mr (Mons. L\'impertinent)')

    # PEOPLE THAT STAY THE SAME.

    def test_make_order_title_name_single(self):
        self.assertEqual(Topic.objects.make_order_title(
            "Shelston", is_person=True),
            "Shelston")

    def test_make_order_title_name_single_parentheses(self):
        self.assertEqual(Topic.objects.make_order_title(
            "Mary (c, Pepys' chambermaid)", is_person=True),
            "Mary (c, Pepys' chambermaid)")

    def test_make_order_title_name_i(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Mary I of England', is_person=True),
            'Mary I of England')

    def test_make_order_title_name_iv(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Philip IV (King of Spain, 1621-1665)', is_person=True),
            'Philip IV (King of Spain, 1621-1665)')

    def test_make_order_title_name_the(self):
        self.assertEqual(Topic.objects.make_order_title(
            'Ivan the Terrible', is_person=True),
            'Ivan the Terrible')
