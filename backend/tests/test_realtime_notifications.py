from unittest.mock import patch, AsyncMock
import pytest
from api.tasks import send_real_time_notification

@patch('api.tasks.get_channel_layer')
@patch('api.tasks.async_to_sync')  # Mock async_to_sync
@pytest.mark.django_db
def test_send_real_time_notification(mock_async_to_sync, mock_channel_layer, create_procurement_officer):
    user = create_procurement_officer

    # Create an AsyncMock for the group_send method
    mock_group_send = AsyncMock()
    mock_channel_layer.return_value.group_send = mock_group_send

    # Mock async_to_sync to simply call the async function directly
    mock_async_to_sync.side_effect = lambda func: func

    send_real_time_notification(user.id, "New notification")

    # Check that the WebSocket notification was sent
    mock_group_send.assert_called_once()
    group_send_args = mock_group_send.call_args[0]
    assert group_send_args[1]['message'] == "New notification"
