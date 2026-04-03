from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType


async def create_notification(
    db: AsyncSession,
    user_id,
    booking_id,
    notification_type: NotificationType,
    message: str,
):
    notification = Notification(
        user_id=user_id,
        booking_id=booking_id,
        type=notification_type,
        message=message,
    )
    db.add(notification)
    await db.flush()
    return notification
