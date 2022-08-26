# Project Name : 🐩Petrasche

### ✌️프로젝트 참여자

- 이민기
- 김주훈
- 엄관용
- 한예슬
- 나성근

### 💻프로젝트 기술 스택

- Python
- Django
- Django RestFramework
- Django Channels
- FastApi
- Tensorflow keras

### 💾DB

- PostgreSQL 14.2

> PostgreSQL 장점


표준 SQL을 준수합니다. SQLite 또는 MySQL보다 PostgreSql은 표준에 좀 더 가깝게 구현하는 것을 목표로 하고 있습니다. <br>
공식 PostgreSql 문서에 따르면 PostgreSql은 전체 핵심 SQL:2011 규정에 필요한 179개의 기능 중 160개를 지원하며 긴 목록의 선택적 기능도 지원합니다.<br>

오픈소스 및 커뮤니티가 이끄는 데이터베이스입니다. <br>
완전한 오픈소스 프로젝트인 PostgreSql의 소스코드는 대규모 헌신적인 커뮤니티에서 개발되었습니다. <br>
Postgres 커뮤니티는 DBMS로 작업하는 방법을 설명하는 공식문서, 위치, 온라인 포럼을 포함한 수많은 리소스를 유지 관리하고 기여합니다.<br>

확장성이 뛰어납니다. 사용자는 카탈로그 기반 작업과 동적 로드 사용을 통해 PostgreSQL을 프로그래밍 방식으로 즉시 확장할 수 있습니다.<br>
공유 라이브러리와 같은 객체 코드 파일을 지정할 수 있고 PostgreSQL은 필요에 따라 이를 로드합니다.<br>

### 주요 코드 안내

<br><br>

> drf serializer 를 통한 json 객체 직렬화

```python
class ArticleSerializer(BaseSerializer):
    article_pet_list = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    like_users = serializers.SerializerMethodField()
    like_num = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    image_lists = serializers.ListField(write_only=True, required=False)
    user_pet = serializers.IntegerField(write_only=True, required=False)
    author = serializers.SerializerMethodField()
    user_following = serializers.SerializerMethodField()
    profile_img = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        comment_lists = []
        for comment in obj.comment_set.all().order_by('-created_at'):
            comment.created_at = time_calculate(datetime.now().timestamp() - comment.created_at.timestamp())
            doc = {
                "id": comment.pk,
                "comment": comment.comment,
                "userid": comment.user.id,
                "username": comment.user.username,
                "created_at": comment.created_at
            }
            comment_lists.append(doc)
        return comment_lists

    def get_profile_img(self, obj):
        user_profiles = UserProfile.objects.filter(user=obj.user.id)
        return [user_profile.profile_img for user_profile in user_profiles]

    def get_user_following(self, obj):
        users = UserFollowing.objects.filter(following_user_id=obj.user.id)
        return [user.user_id.id for user in users]

    def get_article_pet_list(self, obj):
        return [pet.id for pet in obj.petprofile_set.all()]
        
    def get_author(self,obj):
        return obj.user.username

    def get_likes(self, obj):
        return [like.id for like in obj.like.all()]

    def get_like_users(self, obj):
        return [like.username for like in obj.like.all()]

    def get_like_num(self,obj):
        return  obj.like.all().count()

    def get_images(self, obj):
        return [image.imgurl for image in obj.image_set.all()]

    def create(self, validated_data):
        validated_data['content'] = text_re(validated_data['content'])
        try:
            user_pet = validated_data.pop('user_pet')
        except:
            pass
        image_lists = validated_data.pop('image_lists')
        user = validated_data['user']
        user = user.id
        imgurls = []
        for image in image_lists:
            url = s3(user, image)
            imgurls.append(url)
        article = Article(**validated_data)
        article.save()
        for imageurl in imgurls:
            image_data = {'article': article, 'imgurl': imageurl}
            Image.objects.create(**image_data)
            
        # es indexing 
        es_body = {
            "pk": article.pk,
            "title": article.title,
            "content": article.content
        }
        requests.post(es_url+f"/article/_doc/{article.pk}", json=es_body)
              
        # hashtags
        pattern = '#([0-9a-zA-Z가-힣]*)'
        hash_w = re.compile(pattern)

        hashtags = hash_w.findall(article.content)
        es_hashtags_input = ""
        for tag in hashtags:
            es_hashtags_input += " "+tag
            
        es_hashtag_body = {
            "pk": article.pk,
            "hashtags": es_hashtags_input
        }
        requests.post(es_url+f"/hashtag/_doc/{article.pk}", json=es_hashtag_body)

        
        try:
            pet = PetProfile.objects.get(id=user_pet)
            pet.article.add(article)
            pet.save()
        except:
            pass
        return article

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()


        # es update
        es_body = {
            "doc": {
                "title": instance.title,
                "content": instance.content
            }
        }
        requests.post(es_url+f"/article/_update/{instance.pk}", json=es_body)

        
        # es hashtag update
        pattern = '#([0-9a-zA-Z가-힣]*)'
        hash_w = re.compile(pattern)

        hashtags = hash_w.findall(instance.content)
        print("해시태그 추출: ", hashtags)
        es_hashtags_input = ""
        for tag in hashtags:
            print("tag => ", tag)
            es_hashtags_input += " "+tag
        
        es_hashtag_body = {
            "doc": {
                "hashtags": es_hashtags_input
            }
        }
        requests.post(es_url+f"/hashtag/_update/{instance.pk}", json=es_hashtag_body)

        return instance

    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'content', 'is_active', 'images', 'image_lists', 'likes', 'like_num', 'author', 'date', 'user_following','user_pet','article_pet_list','like_users', 'profile_img', 'comments']

```
<br><br>
> boto3를 통한 s3 업로드 구현

```python
def upload(user,image):
    s3 = boto3.client('s3',
        aws_access_key_id=env('AWSAccessKeyId'),
        aws_secret_access_key=env('AWSSecretKey'),
        region_name='ap-northeast-2',
    )

    Bucket = "pracs3"

    now = datetime.datetime.now()
    now = now.strftime('%Y%m%d%H%M%S%f')

    key = f'{user}/{now}.jpg'

    s3.put_object(
        ACL="public-read",
        Bucket=Bucket,
        Body=image,
        Key=key,
        ContentType=image.content_type
        )

    url = f'https://{Bucket}.s3.ap-northeast-2.amazonaws.com/{key}'

    return url

def delete(image):
    s3 = boto3.client('s3',
        aws_access_key_id=env('AWSAccessKeyId'),
        aws_secret_access_key=env('AWSSecretKey'),
        region_name='ap-northeast-2',
    )

    Bucket = "pracs3"

    key = image

    s3.delete_object(
        Bucket=Bucket,
        Key=key,
    )
    return True
```
<br><br>
> Simple Jwt를 이용한 로그인 구현

```python
class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    

class TokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['username'] = user.username

        return token
```

<br><br>

> 기타 기술 내용
- 엘라스틱 서치
- PostgreSQL 쿼리 최적화
- WebSocket 서버를 이용한 채팅 기능 구현
- Tensorflow keras AI 이미지 분류

<br><br>

> 배포 및 아키텍쳐


