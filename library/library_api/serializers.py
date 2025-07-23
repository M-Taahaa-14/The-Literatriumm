from rest_framework import serializers
from library_app.models import Book, BorrowRecord, BookCategory, Review, UserProfile, Notification
from django.contrib.auth.models import User

class UserSignupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'full_name', 'address', 'phone')

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        full_name = validated_data['full_name']
        address = validated_data['address']
        phone = validated_data['phone']
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, full_name=full_name, address=address, phone=phone)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    isbn = serializers.CharField(required=False, allow_blank=True)
    cover_image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Book
        fields = '__all__'
    
    def create(self, validated_data):
        # If ISBN is not provided or is blank, let Django generate it
        if not validated_data.get('isbn'):
            validated_data.pop('isbn', None)  # Remove empty ISBN so default kicks in
            
        # Handle empty cover_image object from frontend
        cover_image = validated_data.get('cover_image')
        if cover_image == {} or cover_image == '' or cover_image is None:
            validated_data.pop('cover_image', None)
            
        return super().create(validated_data)
    
    def to_internal_value(self, data):
        # Handle empty cover_image object before validation
        if 'cover_image' in data and data['cover_image'] == {}:
            data = data.copy()  # Don't modify original data
            data.pop('cover_image')
        return super().to_internal_value(data)

class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = '__all__'


class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = '__all__'

class BorrowRecordUserSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    class Meta:
        model = BorrowRecord
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'book', 'content', 'rating', 'created_at', 'user_name']
        read_only_fields = ['user', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class BookAdminSerializer(serializers.ModelSerializer):
    borrowed_count = serializers.SerializerMethodField()
    isbn = serializers.CharField(required=False, allow_blank=True)
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Book
        fields = '__all__'

    def get_borrowed_count(self, obj):
        return obj.borrowrecord_set.filter(is_returned=False).count()
    
    def create(self, validated_data):
        # If ISBN is not provided or is blank, let Django generate it
        if not validated_data.get('isbn'):
            validated_data.pop('isbn', None)  # Remove empty ISBN so default kicks in
        
        # Handle empty cover_image object from frontend
        cover_image = validated_data.get('cover_image')
        if cover_image == {} or cover_image == '' or cover_image is None:
            validated_data.pop('cover_image', None)
            
        return super().create(validated_data)
    
    def to_internal_value(self, data):
        # Handle empty cover_image object before validation
        if 'cover_image' in data and data['cover_image'] == {}:
            data = data.copy()  # Don't modify original data
            data.pop('cover_image')
        return super().to_internal_value(data)

class BookCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = '__all__'


class BorrowRecordAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = BorrowRecord
        fields = '__all__' 

class ReviewAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    class Meta:
        model = Review
        fields = '__all__'