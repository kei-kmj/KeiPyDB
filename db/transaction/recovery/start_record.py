

class StartRecord:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

    def write_to_log(self, log_manager, tx_number):
        pass