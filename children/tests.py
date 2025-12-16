from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from children.models import Child

User = get_user_model()

class ChildModelTest(TestCase):
    def setUp(self):
        self.parent = User.objects.create_user(username='parent1', password='password')

    def test_create_valid_child(self):
        """Test that a child with valid age (5-11) can be created."""
        child = Child(
            parent=self.parent,
            first_name="Alice",
            age=7,
            school_name="Primary School",
            year_group=3
        )
        child.full_clean() # Should not raise
        child.save()
        self.assertEqual(Child.objects.count(), 1)

    def test_create_child_too_young(self):
        """Test that age < 5 raises validation error."""
        child = Child(
            parent=self.parent,
            first_name="Baby",
            age=4,
            school_name="Nursery",
            year_group=0
        )
        with self.assertRaises(ValidationError):
            child.full_clean()

    def test_create_child_too_old(self):
        """Test that age > 11 raises validation error."""
        child = Child(
            parent=self.parent,
            first_name="Teen",
            age=12,
            school_name="High School",
            year_group=7
        )
        with self.assertRaises(ValidationError):
            child.full_clean()

    def test_year_group_alignment(self):
        """Year group must stay aligned to age bands."""
        child = Child(
            parent=self.parent,
            first_name="Mismatch",
            age=8,
            school_name="Primary School",
            year_group=1,  # invalid for age 8
        )
        with self.assertRaises(ValidationError):
            child.full_clean()

    def test_school_name_required(self):
        """Explicitly reject empty school names."""
        child = Child(
            parent=self.parent,
            first_name="NoSchool",
            age=7,
            school_name="",
            year_group=3,
        )
        with self.assertRaises(ValidationError):
            child.full_clean()

    def test_ownership_security(self):
        """Ensure children are strictly linked to parents."""
        child = Child.objects.create(
            parent=self.parent,
            first_name="Bob",
            age=10,
            school_name="School",
            year_group=5
        )
        self.assertEqual(child.parent, self.parent)

class ChildAccessControlTest(TestCase):
    def setUp(self):
        self.parent1 = User.objects.create_user(username='parent1', password='password')
        self.parent2 = User.objects.create_user(username='parent2', password='password')
        
        self.child1 = Child.objects.create(
            parent=self.parent1, first_name="Alice", age=7, school_name="School A", year_group=3
        )
        self.child2 = Child.objects.create(
            parent=self.parent2, first_name="Bob", age=8, school_name="School B", year_group=4
        )

    def test_list_view_shows_only_own_children(self):
        """Ensure parent1 only sees Alice, not Bob."""
        self.client.login(username='parent1', password='password')
        response = self.client.get(reverse('children:list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertNotContains(response, "Bob")

    def test_update_view_enforces_ownership(self):
        """Parent1 should get 404 when trying to edit Parent2's child."""
        self.client.login(username='parent1', password='password')
        url = reverse('children:update', kwargs={'pk': self.child2.pk})
        
        response = self.client.get(url)
        # Expect 404 because get_queryset filters out objects not owned by user
        self.assertEqual(response.status_code, 404)

    def test_delete_view_enforces_ownership(self):
        """Parent1 should get 404 when trying to delete Parent2's child."""
        self.client.login(username='parent1', password='password')
        url = reverse('children:delete', kwargs={'pk': self.child2.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        
        # Verify object still exists
        self.assertTrue(Child.objects.filter(pk=self.child2.pk).exists())
