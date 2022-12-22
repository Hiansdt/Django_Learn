from django.test import TestCase

import datetime

from django.utils import timezone
from .models import Question
from django.urls import reverse

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_publihed_recently returns False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(),False)

    def test_was_published_recently_with_old_questions(self):
        """
        was_published_recently returns False for old questions.
        """
        time = timezone.now() - datetime.timedelta(days = 1, seconds=1)
        past_question = Question(pub_date=time)
        self.assertIs(past_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_questions(self):
        """
        was_published_recently returns True for recent questions.
        """
        time = timezone.now() - datetime.timedelta(hours = 23, minutes=59, seconds=59)
        past_question = Question(pub_date=time)
        self.assertIs(past_question.was_published_recently(), True)



def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question_text, days, choice_text=0):
    """
    Create question with choices.
    """
    question = create_question(question_text, days)
    if choice_text:
        question.choice_set.create(choice_text=choice_text, votes = 0)
        return question
    else:
        return question

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        In case there isnt any questions, display an appropriate response
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Past questions are displayed in the index page.
        """
        question = create_choice(question_text="Past question.", days=-30, choice_text='Al')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
            Even if both past and future questions exist, only past questions are displayed.
        """
        question = create_choice(question_text="Past question.", days=-30, choice_text='Al')
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_choice(question_text="Past question 1.", days = -30, choice_text='Al')
        question2 = create_choice(question_text="Past question 2.", days = -5, choice_text='ala')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question1, question2],
        )


class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with pub_date in the future returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with pub_date in the past displays the questions's text.
        """
        past_question = create_choice(question_text="Past question.", days=-5, choice_text="OneTwo")
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_without_choices(self):
        """
        Question with no choices return a 404 not found.
        """
        question_without_choices = create_question(question_text="alahtsds", days=-5)
        url = reverse('polls:detail', args=(question_without_choices.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)