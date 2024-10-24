from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import UserDetails  
from accounts.models import Account  

class Command(BaseCommand):
    help = 'Permanently delete soft-deleted users and their accounts after 15 days'

    def handle(self, *args, **options):
        threshold_date = timezone.now() - timedelta(days=15)

        deleted_users = UserDetails.objects.filter(is_deleted=True, deleted_at__lt=threshold_date)
        for user in deleted_users:
            Account.objects.filter(user=user.user).delete()
            user.user.delete() 
            user.delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted old soft-deleted users and their accounts.'))
