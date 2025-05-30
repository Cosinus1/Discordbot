import asyncio
import datetime

# Dictionary to track dead players and their resurrection times
dead_players = {}

class PlayerLifecycleManager:
    """
    Manages player death and resurrection mechanics.
    """
    def __init__(self):
        self.dead_players = {}
        self.resurrection_time_minutes = 5
    
    def mark_player_dead(self, user_id):
        """Mark a player as dead and schedule resurrection"""
        resurrection_time = datetime.datetime.now() + datetime.timedelta(minutes=self.resurrection_time_minutes)
        self.dead_players[user_id] = resurrection_time
        return resurrection_time
    
    def is_player_dead(self, user_id):
        """Check if a player is currently dead"""
        return user_id in self.dead_players and datetime.datetime.now() < self.dead_players[user_id]
    
    def get_resurrection_time(self, user_id):
        """Get the remaining time until resurrection in a formatted string"""
        if user_id in self.dead_players:
            remaining = self.dead_players[user_id] - datetime.datetime.now()
            if remaining.total_seconds() <= 0:
                self.dead_players.pop(user_id, None)
                return None
                
            minutes = int(remaining.total_seconds() // 60)
            seconds = int(remaining.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        return None
    
    def remove_dead_status(self, user_id):
        """Remove a player from the dead_players dictionary"""
        self.dead_players.pop(user_id, None)
    
    async def schedule_resurrection(self, client, user_id, discord_user, update_callback):
        """
        Schedule player resurrection after the configured time
        
        Args:
            client: Discord client for scheduling tasks
            user_id: The user ID to resurrect
            discord_user: The Discord user object
            update_callback: Function to call to update player data when resurrected
        """
        async def resurrect_player():
            # Wait for resurrection time
            await asyncio.sleep(self.resurrection_time_minutes * 60)
            
            # Remove from dead_players dictionary
            self.remove_dead_status(user_id)
            
            # Call the update callback to restore player health
            update_callback(user_id)
            
            # Try to notify the player
            try:
                await discord_user.send("You have been resurrected with full health!")
            except:
                # If DM fails, we don't need to do anything special
                pass
        
        # Start the resurrection task
        client.loop.create_task(resurrect_player())

# Create a singleton instance to be imported by other modules
lifecycle_manager = PlayerLifecycleManager()