from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import datetime

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        access = refresh.access_token

        data['access_expires_at'] = datetime.fromtimestamp(access['exp']).strftime('%Y-%m-%d %H:%M:%S')
        data['refresh_expires_at'] = datetime.fromtimestamp(refresh['exp']).strftime('%Y-%m-%d %H:%M:%S')

        return data