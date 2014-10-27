from django.db import models

# Create your models here.
INTERACTION_CHOICES = (
    (0, 'More awake'),
    (1, 'Less awake'),
    (2, 'More enagaged'),
    (3, 'Less engaged'),
)


class Creature(models.Model):
    name = models.CharField(max_length=255, help_text="Name of this creature")
    eye = models.FileField(help_text="Static image of the eye (JSON)")
    overlay = models.FileField(help_text="Any overay for the eye (JSON)", blank=True, null=True)
    pupil_mask = models.FileField(help_text="Mask showing valid pupil positions", blank=True, null=True)
    image = models.ImageField(blank=True, help_text="Image of the eye", null=True, default=None)
    sclera_color = models.CharField(max_length=6, default='ffffff', help_text="Color of the creature's scelere")
    lid_color = models.CharField(max_length=6, default='000000', help_text="Color of the creature's eyelid")
    circadian_offset = models.FloatField(
        default=0,
        help_text="Offset from equal wake-to-sleep")
    circadian_period = models.FloatField(
        default=20,
        help_text="Period of wake/sleep cycle (minutes)")
    restlessness = models.FloatField(
        default=0.05,
        help_text="How regularly creature will change eyes (percent)")
    maximum_speed = models.FloatField(
        default=1.0,
        help_text="Maximum speed of the creature (percent)")
    minimum_speed = models.FloatField(
        default=0.0,
        help_text="Minimum speed of the creature (percent)")
    maximum_blink = models.IntegerField(
        default=150,
        help_text="Maximum frames between blinks @ 30fps")
    minimum_blink = models.IntegerField(
        default=60,
        help_text="Minimum frames between blinks @ 30fps")

    def __str__(self):
        return self.name


class HeroAnimation(models.Model):
    name = models.CharField(max_length=255, help_text="Name of this animation")
    animation = models.FileField(help_text="Animation (JSON)")
    loops = models.PositiveIntegerField(default=1)
    weight = models.FloatField(
        default=1.0,
        help_text="Weight for this animation")


class CreatureQuestion(models.Model):
    creature = models.ForeignKey(Creature, related_name="questions")
    enabled = models.BooleanField(default=True)
    question = models.TextField(help_text="Question the creature is asking")

    def __str__(self):
        return self.creature.name + ":" + self.question


class CreatureQuestionResponse(models.Model):
    question = models.ForeignKey(CreatureQuestion, related_name="responses")
    response = models.CharField(max_length=100, help_text="Reponse")
    animation = models.FileField(help_text="Animation (JSON)")
    loops = models.PositiveIntegerField(default=1)
    result = models.IntegerField(choices=INTERACTION_CHOICES, default=0)

    def __str__(self):
        return "({}) {} : {}".format(self.question.creature.name, self.question.question, self.response)


class Interaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    response = models.ForeignKey(CreatureQuestionResponse)


class UserCreatedCreature(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    eye = models.TextField()
