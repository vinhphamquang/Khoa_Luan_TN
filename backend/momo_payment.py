"""
Module tích hợp thanh toán MoMo (Sandbox Mode)
Sử dụng MoMo API v2 - REST
"""
import hashlib
import hmac
import uuid
import json
import requests
import time

# ============================================
# MOMO SANDBOX CONFIG
# ============================================
MOMO_CONFIG = {
    'partner_code': 'MOMO',
    'access_key': 'F8BBA842ECF85',
    'secret_key': 'K951B6PE1waDMi640xX08PD3vg6EkVlz',
    'api_endpoint': 'https://test-payment.momo.vn/v2/gateway/api/create',
}

PREMIUM_PRICE = 50000  # 50.000 VNĐ


def create_momo_payment(order_id, amount, order_info, redirect_url, ipn_url):
    """
    Tạo đơn thanh toán MoMo
    Returns: dict {success, payUrl, orderId, message}
    """
    try:
        partner_code = MOMO_CONFIG['partner_code']
        access_key = MOMO_CONFIG['access_key']
        secret_key = MOMO_CONFIG['secret_key']
        request_id = str(uuid.uuid4())
        extra_data = ''
        request_type = 'payWithMethod'

        # Tạo chữ ký HMAC SHA256
        raw_signature = (
            f"accessKey={access_key}"
            f"&amount={amount}"
            f"&extraData={extra_data}"
            f"&ipnUrl={ipn_url}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={partner_code}"
            f"&redirectUrl={redirect_url}"
            f"&requestId={request_id}"
            f"&requestType={request_type}"
        )

        signature = hmac.new(
            secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Tạo request body
        request_body = {
            'partnerCode': partner_code,
            'partnerName': 'SmartFoodAI',
            'storeId': 'SmartFoodAI_Store',
            'requestId': request_id,
            'amount': int(amount),
            'orderId': order_id,
            'orderInfo': order_info,
            'redirectUrl': redirect_url,
            'ipnUrl': ipn_url,
            'lang': 'vi',
            'requestType': request_type,
            'autoCapture': True,
            'extraData': extra_data,
            'signature': signature,
        }

        print(f"[MOMO] Creating payment: orderId={order_id}, amount={amount}")
        print(f"[MOMO] Raw signature: {raw_signature}")

        # Gọi MoMo API
        response = requests.post(
            MOMO_CONFIG['api_endpoint'],
            json=request_body,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        result = response.json()
        print(f"[MOMO] Response: {json.dumps(result, indent=2)}")

        if result.get('resultCode') == 0:
            return {
                'success': True,
                'payUrl': result.get('payUrl', ''),
                'orderId': order_id,
                'requestId': request_id,
                'message': 'Tạo đơn thanh toán thành công'
            }
        else:
            return {
                'success': False,
                'message': result.get('message', 'Lỗi tạo đơn thanh toán MoMo'),
                'resultCode': result.get('resultCode')
            }

    except Exception as e:
        print(f"[MOMO ERROR] {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'Lỗi kết nối MoMo: {str(e)}'
        }


def verify_momo_signature(data):
    """
    Xác thực chữ ký IPN callback từ MoMo
    Returns: bool
    """
    try:
        secret_key = MOMO_CONFIG['secret_key']
        access_key = MOMO_CONFIG['access_key']

        raw_signature = (
            f"accessKey={access_key}"
            f"&amount={data.get('amount', '')}"
            f"&extraData={data.get('extraData', '')}"
            f"&message={data.get('message', '')}"
            f"&orderId={data.get('orderId', '')}"
            f"&orderInfo={data.get('orderInfo', '')}"
            f"&orderType={data.get('orderType', '')}"
            f"&partnerCode={data.get('partnerCode', '')}"
            f"&payType={data.get('payType', '')}"
            f"&requestId={data.get('requestId', '')}"
            f"&responseTime={data.get('responseTime', '')}"
            f"&resultCode={data.get('resultCode', '')}"
            f"&transId={data.get('transId', '')}"
        )

        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        received_signature = data.get('signature', '')

        is_valid = expected_signature == received_signature
        print(f"[MOMO VERIFY] Valid={is_valid}, OrderId={data.get('orderId')}")

        return is_valid

    except Exception as e:
        print(f"[MOMO VERIFY ERROR] {e}")
        return False


def generate_order_id(user_id):
    """Tạo mã đơn hàng duy nhất"""
    timestamp = int(time.time())
    return f"SF_{user_id}_{timestamp}"
