from app.config import settings

class CurrencyManager:
    def __init__(self):
        # Track balances per client (could be websocket ID, user ID, etc.)
        self._balances = {}

    def register_client(self, client_id):
        """Initialize a client with starting tokens."""
        self._balances[client_id] = settings.STARTING_TOKENS

    def remove_client(self, client_id):
        """Clean up when a client disconnects."""
        self._balances.pop(client_id, None)

    def get_balance(self, client_id):
        return self._balances.get(client_id, 0)

    def calculate_cost(self, queue_length: int) -> int:
        """Cost = 0 if queue empty, else queueLength + costModifier (modifier doubles every 5 songs)."""
        if queue_length == 0:
            return 0

        # Determine modifier based on queue length
        steps = (queue_length - 1) // 5  # every 5 songs, modifier doubles
        modifier = settings.COST_MODIFIER * (2 ** steps)
        return queue_length + modifier

    def try_spend(self, client_id, queue_length: int) -> tuple[bool, int]:
        """Attempt to spend tokens for adding a song. Returns (success, new_balance)."""
        cost = self.calculate_cost(queue_length)
        balance = self.get_balance(client_id)

        if balance >= cost:
            self._balances[client_id] = balance - cost
            print(f"Client {client_id} spent {cost} tokens, new balance: {self._balances[client_id]}")
            return True, self._balances[client_id]
        return False, balance
    
    def reward_for_popular_track(self, owner_id: str, tokens: int = settings.POPULAR_TRACK_REWARD) -> int:
        """Reward the owner of a track with tokens when it reaches supermajority likes."""
        if owner_id not in self._balances:
            return 0
        self._balances[owner_id] += tokens
        return self._balances[owner_id]
    
    def add_tokens(self, client_id, tokens: int):
        """Add tokens to a client's balance."""
        if client_id in self._balances:
            self._balances[client_id] += tokens
            print(f"Client {client_id} received {tokens} tokens, new balance: {self._balances[client_id]}")
