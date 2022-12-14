from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
from django.conf import settings
from pytz import timezone

class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def created_at_korean_time(self):
        korean_timezone = timezone(settings.TIME_ZONE)
        return self.created_at.astimezone(korean_timezone)

    class Meta:
        abstract = True #abstractbaseclass가 되도록


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError('Users must have an username')
        user = self.model(
            email=email,
            username=username,
            password=password,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            email=email,
            username=username,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# Create your models here.
class User(BaseModel, AbstractBaseUser):
    username = models.CharField("닉네임", max_length=20, unique=True)
    password = models.CharField("패스워드", max_length=128, null=True)
    email = models.EmailField("이메일", max_length=100, default='', unique=True)
    latitude = models.FloatField("위도", default=0.0, null=True)
    longitude = models.FloatField("경도", default=0.0, null=True)
    is_active = models.BooleanField(default=True)

    # is_staff에서 해당 값 사용
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # id로 사용 할 필드 지정.
    # 로그인 시 USERNAME_FIELD에 설정 된 필드와 password가 사용된다.
    USERNAME_FIELD = 'email'

    # user를 생성할 때 입력받은 필드 지정
    REQUIRED_FIELDS = ['username']

    objects = UserManager()  # custom user 생성 시 필요

    def __str__(self):
        return f"{self.username}"

    # 로그인 사용자의 특정 테이블의 crud 권한을 설정, perm table의 crud 권한이 들어간다.
    # admin일 경우 항상 True, 비활성 사용자(is_active=False)의 경우 항상 False
    def has_perm(self, perm, obj=None):
        return True

    # 로그인 사용자의 특정 app에 접근 가능 여부를 설정, app_label에는 app 이름이 들어간다.
    # admin일 경우 항상 True, 비활성 사용자(is_active=False)의 경우 항상 False
    def has_module_perms(self, app_label):
        return True

    # admin 권한 설정
    @property
    def is_staff(self):
        return self.is_admin

class UserProfile(models.Model):
    gender_choice = (
        ('1', '남자'),
        ('2', '여자'),
    )
    user = models.OneToOneField(User, verbose_name="유저", on_delete=models.CASCADE) 
    birthday = models.DateField("생년월일", blank=True, null=True)
    gender = models.CharField("성별", max_length=5, choices=gender_choice, null=True, blank=True)
    is_active= models.BooleanField("공개여부", default=True, null=True, blank=True)
    phoneNumberRegex = RegexValidator(regex = r'^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$')
    phone = models.CharField("폰 번호",validators = [phoneNumberRegex], max_length = 13, unique = True, null=True, blank=True)
    introduction = models.TextField("자기 소개글", null=True, blank=True, default="유저님의 마이 페이지입니다")
    address = models.TextField("주소", null=True, blank=True)
    profile_img = models.URLField("프로필 이미지", max_length=500, null=True, blank=True, default="https://cdn.pixabay.com/photo/2017/09/25/13/12/cocker-spaniel-2785074__480.jpg" )



class UserFollowing(models.Model):
    user_id = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at= models.DateTimeField(auto_now_add=True)

class PetProfile(BaseModel):
    type_choice = (
        ('1', '강아지'),
        ('2', '고양이'),
        ('3', '기타'),
    )

    gender_choice = (
        ('1', '남자'),
        ('2', '여자'),
        ('3', '모름'),
    )

    size_choice = (
        ('1', '소형'),
        ('2', '중형'),
        ('3', '대형'),
    )
    user = models.ForeignKey(User, related_name="parent", on_delete=models.CASCADE)
    name = models.CharField("이름", max_length=20)
    birthday = models.DateField("생년월일", blank=True, null=True)
    type = models.CharField("종류", max_length=5, choices=type_choice)
    gender = models.CharField("성별", max_length=5, choices=gender_choice, default='3')
    size = models.CharField("사이즈", max_length=5, choices=size_choice)
    pet_profile_img = models.URLField("프로필 이미지", max_length=200, null=True, blank=True, default="https://cdn.pixabay.com/photo/2017/09/25/13/12/cocker-spaniel-2785074__480.jpg" )
    article = models.ManyToManyField('article.Article', verbose_name="게시물")

    def __str__(self):
        return f"{self.user.username}님의 {self.name}"
    
