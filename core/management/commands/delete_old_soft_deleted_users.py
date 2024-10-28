from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import UserDetails  
from accounts.models import Account  
from categories.models import Categories

class Command(BaseCommand):
    help = 'Permanently delete soft-deleted users, their accounts, and categories after 15 days'

    def handle(self, *args, **options):
        # Calculate the threshold date (15 days ago)
        threshold_date = timezone.now() - timedelta(days=15)

        # Find all users who are soft-deleted and were deleted more than 15 days ago
        deleted_users = UserDetails.objects.filter(is_deleted=True, deleted_at__lt=threshold_date)

        for user_detail in deleted_users:
            user = user_detail.user 

            Categories.objects.filter(user=user).delete()
            Account.objects.filter(user=user).delete()

            user.delete()
            user_detail.delete()

            self.stdout.write(self.style.SUCCESS(f'Successfully deleted user {user.username}, their accounts, and categories.'))

        self.stdout.write(self.style.SUCCESS('Successfully deleted all old soft-deleted users, their accounts, and categories.'))
