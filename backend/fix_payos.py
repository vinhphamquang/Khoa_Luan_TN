import sys
sys.path.append('d:/KLTN/backend')
from app import app
from db_queries import get_db_connection, update_payment_status, upgrade_user_account, get_payment_by_order_id
from payos_payment import payos_client
import json

def fix_pending_payments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT madonhang, manguoidung FROM ThanhToan WHERE trangthai='pending' AND phuongthuc='payos'")
    payments = cursor.fetchall()
    
    for p in payments:
        order_id = p[0]
        manguoidung = p[1]
        try:
            link_info = payos_client.getPaymentLinkInformation(order_id)
            if getattr(link_info, 'status', None) == 'PAID':
                print(f'Order {order_id} is PAID. Updating...')
                trans_id = str(getattr(link_info.transactions[0], 'reference', '')) if hasattr(link_info, 'transactions') and getattr(link_info, 'transactions', None) else ''
                
                response_data = ''
                if hasattr(link_info, 'model_dump_json'):
                    response_data = link_info.model_dump_json()
                elif hasattr(link_info, 'dict'):
                    response_data = json.dumps(link_info.dict(), ensure_ascii=False)
                    
                update_payment_status(order_id, 'success', trans_id, response_data)
                upgrade_user_account(manguoidung)
                print('Successfully upgraded user', manguoidung)
            else:
                print(f'Order {order_id} status is {getattr(link_info, "status", "UNKNOWN")}')
        except Exception as e:
            print(f'Error processing {order_id}: {e}')

if __name__ == '__main__':
    fix_pending_payments()
