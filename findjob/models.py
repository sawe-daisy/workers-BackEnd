from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from cloudinary.models import CloudinaryField
# from pinax.notifications import models as Notification
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.save()

        return user

class Role(models.Model):
    WORKER = 1
    EMPLOYER = 2
    ADMIN = 3
    ROLE_CHOICES = (
        (WORKER, 'worker'),
        (EMPLOYER, 'employer'),
        (ADMIN, 'admin'),
        )

    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):        
        return self.get_id_display()


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role)


 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):     
        return self.email

    @property
    def get_full_name(self):       
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, default=' ', blank=True)
    last_name = models.CharField(max_length=50, default=' ', blank=True)
    picture = CloudinaryField('Image')
    location = models.CharField(max_length=50, default=' ', blank=True)
    account_type = models.CharField(max_length=50, default=' ', blank=True)


    def save(self, *args, **kwargs):
	    super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class jobcategory(models.Model):
    job_category = models.CharField(max_length=100)

    
    def __str__(self):
        return f' {self.job_category} jobcategory'


    def create_category(self):
        self.save()

    def delete_category(self):
        self.delete()
                   
    @classmethod
    def find_category_by_id(cls,id):
        category_result = cls.objects.get(id=id)
        return category_result


class Jobpost(models.Model):

    user = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)    
    post_pic = CloudinaryField('Image')
    job_category = models.ForeignKey(jobcategory, on_delete=models.CASCADE, related_name='jobcategory')
    job_description = models.CharField(max_length=100)    
    contact = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return f' {self.title} Post'


    def create_post(self):
        self.save()

    def delete_post(self):
        self.delete()
                   
    @classmethod
    def find_post_by_id(cls,id):
        post_result = cls.objects.get(id=id)
        return post_result

    @classmethod
    def find_post_by_location(cls,location):
        post_result = cls.objects.get(location=location)
        return post_result

    @classmethod
    def find_post_by_category(cls,job_category):
        post_result = cls.objects.get(job_category=job_category)
        return post_result
 
    @classmethod
    def update_post(cls,current_value,new_value):
        fetched_object = cls.objects.filter(count=current_value).update(count=new_value)
        return fetched_object


    @classmethod
    def retrieve_all(cls):
        all_objects = Jobpost.objects.all()
        for item in all_objects:
            return item
        
class Reviews(models.Model):
    Jobpost = models.ForeignKey(Jobpost,on_delete=models.CASCADE,related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)


    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'reviews {} by {}'.format(self.body, self.name)

    def user_review_post(sender, instance, *args, **kwargs):
        review = instance
        post = review.post
        text_preview = review.body[:90]
        sender = review.user
        # notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview ,notification_type=2)
        notify.save()

    def user_del_review_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        # notify = Notification.objects.filter(post=post, sender=sender, notification_type=2)
        notify.delete()
#Review
post_save.connect(Reviews.user_review_post, sender=Reviews)
post_delete.connect(Reviews.user_del_review_post, sender=Reviews)




