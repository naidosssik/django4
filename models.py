from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

# from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    name = models.CharField('Название роли', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True, null=True)
    
    class Meta:
        verbose_name = _('Роль')
        verbose_name_plural = _('Роли')
        
    def __str__(self):
        return self.name


class Nomination(models.Model):
    name = models.CharField(_('Название номинации'), max_length=200)
    description = models.TextField(_('Описание'), blank=True)
    created_date = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    end_date = models.DateTimeField(_('Дата завершения'), blank=True, null=True)

    class Meta:
        verbose_name = _('Номинация')
        verbose_name_plural = _('Номинации')
        
    @property
    def is_currently_active(self):
        now = timezone.now()
        if self.end_date:
            return self.created_date <= now <= self.end_date
        return self.created_date <= now

    def clean(self):
        if self.end_date and self.end_date < self.created_date:
            raise ValidationError('Дата завершения не может быть раньше даты создания.')


    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(_('Имя'), max_length=30, blank=True)
    surname = models.CharField(_('Фамилия'), max_length=30, blank=True)
    email = models.EmailField(_('Электронная почта'), unique=True)
    role = models.ForeignKey(Role, verbose_name='Роль', on_delete=models.PROTECT, related_name='users')
    subscriptions = models.ManyToManyField(
        Nomination,
        through='Subscription',
        through_fields=('user', 'nomination'),
        related_name='subscribed_users',
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.name} {self.surname} ({self.role.name})"



class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'nomination')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user.email} подписан на {self.nomination.name}"
    

class Nominee(models.Model):
    nomination = models.ForeignKey(Nomination, verbose_name=_('Номинация'), on_delete=models.CASCADE, related_name='nominees')
    user = models.ForeignKey(User, verbose_name=_('Пользователь-номинант'), on_delete=models.CASCADE, related_name='nominee_profiles')
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Пользователь-номинант'), on_delete=models.CASCADE)
    project_name = models.CharField(_('Название проекта'), max_length=200)
    description = models.TextField(_('Описание проекта'), blank=True)
    contact = models.EmailField(_('Контактный email'), blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Дата создания', default=timezone.now)
    attachment = models.FileField(
        _('Вложение'),
        upload_to='nominee_files/',
        blank=True,
        null=True,
        help_text='Загрузите файл с описанием проекта'
    )


    class Meta:
        verbose_name = _('Номинант')
        verbose_name_plural = _('Номинанты')
        ordering = ['-created_at']
        unique_together = ('nomination', 'user')
        
    def is_new(self):
        return timezone.now() <= self.created_at + timezone.timedelta(days=30)

    def votes_count(self):
        return self.votes.count()

    def yes_votes_count(self):
        return self.votes.filter(choice='Y').count()

    def no_votes_count(self):
        return self.votes.filter(choice='N').count()

    def abstain_votes_count(self):
        return self.votes.filter(choice='A').count()
    
#    def get_absolute_url(self):
#        return reverse('nominee_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.project_name} ({self.user.email})"


class YesVoteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(choice='Y')

class NoVoteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(choice='N')
    
class Vote(models.Model):
    VOTE_CHOICES = [
        ('Y', 'За'),
        ('N', 'Против'),
        ('A', 'Воздержался'),
    ]
    
    user = models.ForeignKey(User, verbose_name=_('Пользователь'), on_delete=models.CASCADE, related_name='votes')
    nominee = models.ForeignKey(Nominee, verbose_name=_('Номинант'), on_delete=models.CASCADE, related_name='votes')
    voted_at = models.DateTimeField(_('Дата голосования'), auto_now_add=True)
    choice = models.CharField(max_length=1, choices=VOTE_CHOICES, default='Y')
    
    objects = models.Manager()
    yes_votes = YesVoteManager()
    no_votes = NoVoteManager()

    class Meta:
        verbose_name = _('Голос')
        verbose_name_plural = _('Голоса')
        unique_together = ('user', 'nominee')

    def __str__(self):
        return f"Голос пользователя {self.user.email} за {self.nominee.project_name}"

class AbstainVoteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(choice='A')

Vote.abstain_votes = AbstainVoteManager()

class Jury(models.Model):
    user = models.OneToOneField(User, verbose_name=_('Пользователь - член жюри'), on_delete=models.CASCADE, related_name='jury_profile')
    bio = models.TextField(_('Биография'), blank=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    class Meta:
        verbose_name = _('Член жюри')
        verbose_name_plural = _('Члены жюри')

    def __str__(self):
        return f"Жюри: {self.user.email}"


class JuryEvaluation(models.Model):
    jury = models.ForeignKey(Jury, verbose_name=_('Член жюри'), on_delete=models.CASCADE, related_name='evaluations')
    nominee = models.ForeignKey(Nominee, verbose_name=_('Номинант'), on_delete=models.CASCADE, related_name='jury_evaluations')
    score = models.PositiveSmallIntegerField(_('Оценка'), default=0)
    comment = models.TextField(_('Комментарий'), blank=True)
    evaluated_at = models.DateTimeField(_('Дата оценки'), auto_now_add=True)

    class Meta:
        verbose_name = _('Оценка жюри')
        verbose_name_plural = _('Оценки жюри')
        unique_together = ('jury', 'nominee')

    def __str__(self):
        return f"Оценка {self.score} от {self.jury.user.email} для {self.nominee.project_name}"

class NKexam(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название экзамена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания текущей записи')
    exam_date = models.DateField(verbose_name='Дата проведения экзамена')
    exam_task = models.ImageField(upload_to='exam_images/', verbose_name='Задание к экзамену')
    users = models.ManyToManyField(User, related_name='exams', verbose_name='Пользователи')
    is_public = models.BooleanField(default=False, verbose_name='Опубликовано')
    
    def __str__(self):
        return self.name
