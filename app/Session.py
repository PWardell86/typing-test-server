class Session:
    def __init__(self, c1_id, c2_id):
        self.c1_ready = False
        self.c2_ready = False
        self.c1_id = c1_id
        self.c2_id = c2_id
        self.buff1 = []
        self.buff2 = []
    
    def write_buffer(self, client_id: str, msg: str) -> None:
        if len(msg) == 0: return
        if client_id == self.c1_id:
            self.buff1.append(msg)
            return 
        self.buff2.append(msg)

    def read_buffer(self, client_id: str) -> str:
        if client_id == self.c2_id:
            return self.buff1
        return self.buff2
